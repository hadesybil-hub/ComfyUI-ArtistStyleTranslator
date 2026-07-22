"""Tests for the V1.7 validated artist knowledge-record foundation."""

from copy import deepcopy
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v170_knowledge_tests"
    spec = spec_from_file_location(
        package_name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load project package")
    package = module_from_spec(spec)
    sys.modules[package_name] = package
    spec.loader.exec_module(package)
    return (
        import_module(f"{package_name}.knowledge_base"),
        import_module(f"{package_name}.artist_database"),
        import_module(f"{package_name}.providers.builtin_provider"),
    )


knowledge, database, builtin_provider = load_project_modules()


def sample_record():
    return database.get_knowledge_record("WLOP")


def unique_record(name="V1.7 Validation Artist", artist_id="v17-validation-artist"):
    record = sample_record()
    record["artist_id"] = artist_id
    record["canonical_name"] = name
    record["display_name"] = name
    record["aliases"] = ()
    record["localized_names"] = {}
    record["semantic"]["evidence"][0]["evidence_id"] = (
        f"legacy:{artist_id}:profile"
    )
    return record


class KnowledgeRecordSchemaTests(unittest.TestCase):
    def test_all_legacy_records_use_complete_v170_schema(self):
        legacy_records = tuple(
            record
            for record in database.KNOWLEDGE_RECORDS
            if record["metadata"]["source"] == "legacy_migration"
        )
        self.assertEqual(len(legacy_records), 31)
        for record in legacy_records:
            self.assertIs(knowledge.validate_knowledge_record(record), record)
            self.assertEqual(set(record), set(knowledge.KNOWLEDGE_RECORD_FIELDS))
            self.assertEqual(
                set(record["metadata"]),
                set(knowledge.KNOWLEDGE_METADATA_FIELDS),
            )
            self.assertEqual(
                set(record["semantic"]),
                set(knowledge.KNOWLEDGE_SEMANTIC_FIELDS),
            )
            self.assertEqual(
                set(record["semantic"]["style_profile"]),
                set(knowledge.STYLE_PROFILE_FIELDS),
            )
            self.assertEqual(
                set(record["semantic"]["category_confidence"]),
                set(knowledge.STYLE_PROFILE_FIELDS),
            )
            self.assertEqual(record["metadata"]["source"], "legacy_migration")
            self.assertEqual(record["metadata"]["review_status"], "published")
            self.assertTrue(record["semantic"]["evidence"])
            self.assertEqual(
                record["semantic"]["evidence"][0]["type"],
                "legacy_migration",
            )

    def test_style_profile_rejects_missing_and_unknown_dimensions(self):
        missing = sample_record()
        del missing["semantic"]["style_profile"]["lighting"]
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(missing)

        unknown = sample_record()
        unknown["semantic"]["style_profile"]["prompt"] = ("forbidden",)
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(unknown)

    def test_confidence_rejects_invalid_profile_and_category_values(self):
        invalid_values = (True, -0.01, 1.01, math.nan, math.inf, "0.95")
        for value in invalid_values:
            with self.subTest(profile_confidence=value):
                record = sample_record()
                record["semantic"]["profile_confidence"] = value
                with self.assertRaises(knowledge.KnowledgeRecordValidationError):
                    knowledge.validate_knowledge_record(record)

            with self.subTest(category_confidence=value):
                record = sample_record()
                record["semantic"]["category_confidence"]["lighting"] = value
                with self.assertRaises(knowledge.KnowledgeRecordValidationError):
                    knowledge.validate_knowledge_record(record)

    def test_evidence_must_be_nonempty_and_structurally_valid(self):
        empty = sample_record()
        empty["semantic"]["evidence"] = ()
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(empty)

        malformed = sample_record()
        del malformed["semantic"]["evidence"][0]["reference"]
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(malformed)

        invalid_scope = sample_record()
        invalid_scope["semantic"]["evidence"][0]["scope"] = "prompt"
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(invalid_scope)

    def test_invalid_dates_version_schema_and_review_status_are_rejected(self):
        cases = (
            ("created_at", "2026-99-99"),
            ("updated_at", "not-a-date"),
            ("version", "1.0"),
            ("profile_schema_version", "9.0"),
            ("review_status", "approved"),
        )
        for field_name, value in cases:
            with self.subTest(field=field_name):
                record = sample_record()
                record["metadata"][field_name] = value
                with self.assertRaises(knowledge.KnowledgeRecordValidationError):
                    knowledge.validate_knowledge_record(record)

        reversed_dates = sample_record()
        reversed_dates["metadata"]["created_at"] = "2026-07-23"
        reversed_dates["metadata"]["updated_at"] = "2026-07-22"
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(reversed_dates)


class KnowledgeBaseLoaderTests(unittest.TestCase):
    def test_artist_id_canonical_name_and_alias_conflicts_fail_explicitly(self):
        first = unique_record()

        duplicate_id = unique_record(
            name="Different Canonical Artist",
            artist_id=first["artist_id"],
        )
        with self.assertRaises(knowledge.KnowledgeBaseConflictError):
            knowledge.KnowledgeBaseLoader((first, duplicate_id))

        duplicate_canonical = unique_record(
            name=first["canonical_name"],
            artist_id="different-canonical-id",
        )
        with self.assertRaises(knowledge.KnowledgeBaseConflictError):
            knowledge.KnowledgeBaseLoader((first, duplicate_canonical))

        alias_collision = unique_record(
            name="Different Alias Artist",
            artist_id="different-alias-id",
        )
        alias_collision["aliases"] = (" V1.7-Validation Artist ",)
        with self.assertRaises(knowledge.KnowledgeBaseConflictError):
            knowledge.KnowledgeBaseLoader((first, alias_collision))

    def test_unicode_nfkc_case_space_and_separator_lookup_is_preserved(self):
        self.assertEqual(database.get_artist("  ＷＬＯＰ  ")["canonical_name"], "WLOP")
        self.assertEqual(database.get_artist("coffee kizoku")["canonical_name"], "Coffee-kizoku")
        self.assertEqual(database.get_artist("TONY-TAKA")["canonical_name"], "Tony Taka")

    def test_only_published_records_enter_runtime(self):
        for status in ("draft", "reviewed"):
            with self.subTest(status=status):
                record = unique_record()
                record["metadata"]["review_status"] = status
                loader = knowledge.KnowledgeBaseLoader((record,))
                self.assertEqual(loader.list_artists(), [])
                self.assertIsNone(loader.get_artist(record["canonical_name"]))
                with self.assertRaises(knowledge.KnowledgeRecordValidationError):
                    knowledge.project_semantic_style_profile(record)
                with self.assertRaises(knowledge.KnowledgeRecordValidationError):
                    knowledge.legacy_artist_view(record)

    def test_legacy_and_knowledge_queries_return_defensive_copies(self):
        legacy = database.get_artist("WLOP")
        legacy["style_profile"]["medium"] = ("mutated",)
        self.assertNotEqual(
            database.get_artist("WLOP")["style_profile"]["medium"],
            ("mutated",),
        )

        record = database.get_knowledge_record("WLOP")
        record["metadata"]["source"] = "mutated"
        self.assertEqual(
            database.get_knowledge_record("WLOP")["metadata"]["source"],
            "legacy_migration",
        )

    def test_list_artists_preserves_count_and_sort_order(self):
        artists = database.list_artists()
        self.assertEqual(len(artists), 37)
        self.assertEqual(artists, sorted(artists, key=str.casefold))


class KnowledgeProjectionTests(unittest.TestCase):
    def test_projection_matches_existing_builtin_provider_for_all_artists(self):
        provider = builtin_provider.BuiltinSemanticProvider()
        legacy_artists = tuple(
            record["canonical_name"]
            for record in database.KNOWLEDGE_RECORDS
            if record["metadata"]["source"] == "legacy_migration"
        )
        for artist in legacy_artists:
            with self.subTest(artist=artist):
                projected = database.project_artist_profile(artist)
                existing = provider.get_profile(artist)
                self.assertEqual(projected, existing)
                self.assertEqual(projected.confidence, 0.95)
                self.assertEqual(
                    projected.evidence,
                    ("builtin structured style profile",),
                )
                self.assertTrue(
                    all(feature.confidence == 0.95 for feature in projected.features)
                )
                self.assertTrue(
                    all(
                        feature.evidence == ("builtin structured style profile",)
                        for feature in projected.features
                    )
                )

    def test_category_confidence_projects_without_exposing_full_evidence(self):
        record = unique_record()
        record["semantic"]["category_confidence"]["lighting"] = 0.61
        record["semantic"]["evidence"][0]["summary"] = (
            "Management-only structured research detail"
        )

        projected = knowledge.project_semantic_style_profile(record)
        lighting = tuple(
            feature for feature in projected.features
            if feature.category == "lighting"
        )

        self.assertTrue(lighting)
        self.assertTrue(all(feature.confidence == 0.61 for feature in lighting))
        self.assertNotIn(
            "Management-only structured research detail",
            projected.evidence,
        )


if __name__ == "__main__":
    unittest.main()
