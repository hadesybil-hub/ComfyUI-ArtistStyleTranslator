"""Data-level review and publishing gates for future artist records."""

from copy import deepcopy
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v172_workflow_tests"
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
        import_module(f"{package_name}.artist_database"),
        import_module(f"{package_name}.knowledge_base"),
        import_module(f"{package_name}.providers.builtin_provider"),
    )


database, knowledge, builtin_provider = load_project_modules()


def homare_record():
    return database.get_knowledge_record("Homare")


class ArtistReviewValidationTests(unittest.TestCase):
    def test_incomplete_profile_is_rejected(self):
        record = homare_record()
        del record["semantic"]["style_profile"]["lighting"]

        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(record)

    def test_missing_evidence_is_rejected(self):
        record = homare_record()
        record["semantic"]["evidence"] = ()

        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(record)

    def test_invalid_review_status_is_rejected(self):
        record = homare_record()
        record["metadata"]["review_status"] = "approved"

        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.validate_knowledge_record(record)

    def test_alias_conflict_is_rejected(self):
        first = homare_record()
        conflicting = deepcopy(first)
        conflicting["artist_id"] = "different-artist"
        conflicting["canonical_name"] = "Different Artist"
        conflicting["display_name"] = "Different Artist"
        conflicting["aliases"] = ("homare works",)
        conflicting["localized_names"] = {}

        with self.assertRaises(knowledge.KnowledgeBaseConflictError):
            knowledge.KnowledgeBaseLoader((first, conflicting))

    def test_artist_name_in_visual_profile_is_rejected(self):
        record = homare_record()
        record["semantic"]["style_profile"]["medium"] = (
            "Homare-inspired digital illustration",
        )

        with self.assertRaisesRegex(
            knowledge.KnowledgeRecordValidationError,
            "artist name",
        ):
            knowledge.validate_knowledge_record(record)

    def test_attribution_and_static_prompt_templates_are_rejected(self):
        invalid_values = (
            "in the style of a named creator",
            "masterpiece, best quality, 8k",
            "portrait --ar 2:3",
            "<lora:example:1.0>",
            "steps: 30, cfg scale: 7",
        )
        for value in invalid_values:
            with self.subTest(value=value):
                record = homare_record()
                record["semantic"]["style_profile"]["medium"] = (value,)
                with self.assertRaisesRegex(
                    knowledge.KnowledgeRecordValidationError,
                    "static prompt syntax",
                ):
                    knowledge.validate_knowledge_record(record)

    def test_review_checklist_is_computed_without_new_record_fields(self):
        record = homare_record()
        self.assertEqual(
            set(record),
            set(knowledge.KNOWLEDGE_RECORD_FIELDS),
        )

        record["metadata"]["review_status"] = "draft"
        draft = knowledge.build_artist_review_checklist(record)
        self.assertEqual(
            tuple(draft),
            knowledge.ARTIST_REVIEW_CHECKLIST_FIELDS,
        )
        self.assertTrue(draft["identity_verified"])
        self.assertTrue(draft["evidence_verified"])
        self.assertTrue(draft["semantic_profile_verified"])
        self.assertFalse(draft["runtime_verified"])
        self.assertFalse(draft["publish_ready"])

        record["metadata"]["review_status"] = "reviewed"
        reviewed = knowledge.build_artist_review_checklist(record)
        self.assertTrue(reviewed["runtime_verified"])
        self.assertTrue(reviewed["publish_ready"])

    def test_reviewed_record_has_explicit_nonproduction_projection(self):
        record = homare_record()
        record["metadata"]["review_status"] = "reviewed"
        loader = knowledge.KnowledgeBaseLoader((record,))

        self.assertIsNone(loader.get_knowledge_record("Homare"))
        review_record = loader.get_knowledge_record(
            "Homare",
            include_reviewed=True,
        )
        self.assertIsNotNone(review_record)
        with self.assertRaises(knowledge.KnowledgeRecordValidationError):
            knowledge.project_semantic_style_profile(review_record)
        profile = knowledge.project_semantic_style_profile(
            review_record,
            allow_reviewed=True,
        )
        self.assertTrue(profile.features)


class PublishingBoundaryTests(unittest.TestCase):
    def test_draft_does_not_enter_builtin_provider(self):
        record = homare_record()
        record["metadata"]["review_status"] = "draft"
        loader = knowledge.KnowledgeBaseLoader((record,))
        provider = builtin_provider.BuiltinSemanticProvider()

        with patch.object(builtin_provider, "get_artist", loader.get_artist):
            self.assertFalse(provider.supports("Homare"))
            with self.assertRaises(builtin_provider.SemanticProviderError):
                provider.get_profile("Homare")

    def test_published_record_enters_builtin_provider(self):
        record = homare_record()
        loader = knowledge.KnowledgeBaseLoader((record,))
        provider = builtin_provider.BuiltinSemanticProvider()

        with patch.object(builtin_provider, "get_artist", loader.get_artist):
            self.assertTrue(provider.supports("Homare"))
            self.assertTrue(provider.get_profile("Homare").features)


if __name__ == "__main__":
    unittest.main()
