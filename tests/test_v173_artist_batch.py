"""Integration and prompt-golden coverage for the V1.7.3 artist batch."""

from copy import deepcopy
import hashlib
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v173_batch_tests"
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
    return {
        name: import_module(f"{package_name}.{name}")
        for name in (
            "artist_database",
            "knowledge_base",
            "nodes",
            "prompt_builder",
            "providers.builtin_provider",
            "resolver",
        )
    }


modules = load_project_modules()
database = modules["artist_database"]
knowledge = modules["knowledge_base"]
nodes = modules["nodes"]
prompt_builder = modules["prompt_builder"]
builtin_provider = modules["providers.builtin_provider"]
resolver_module = modules["resolver"]

BATCH_IDENTITIES = {
    "Oda Non": {
        "artist_id": "oda-non",
        "display_name": "織田non",
        "aliases": ("odanondesu",),
        "localized_names": {
            "ja": ("織田non", "おだ のん"),
            "zh-Hans": ("织田non",),
        },
        "queries": (
            "Oda Non",
            " oda non ",
            "織田non",
            "おだ のん",
            "织田non",
            "odanondesu",
        ),
    },
    "十六夜清心": {
        "artist_id": "izayoi-seishin",
        "display_name": "十六夜清心",
        "aliases": (),
        "localized_names": {},
        "queries": ("十六夜清心", " 十六夜清心 "),
    },
    "LINDA": {
        "artist_id": "linda",
        "display_name": "LINDA",
        "aliases": ("lindacomic",),
        "localized_names": {"ja": ("リンダ",)},
        "queries": ("LINDA", "linda", "lindacomic", "リンダ"),
    },
    "灰司": {
        "artist_id": "hyji",
        "display_name": "灰司",
        "aliases": ("hyji", "hyjihyji"),
        "localized_names": {"ja": ("ハイジ",)},
        "queries": ("灰司", "hyji", "hyjihyji", "ハイジ"),
    },
    "碧木誠心": {
        "artist_id": "aoki-seishin",
        "display_name": "碧木誠心",
        "aliases": (),
        "localized_names": {"ja": ("アオキセイシン",)},
        "queries": ("碧木誠心", "アオキセイシン"),
    },
}

BATCH_ARTISTS = tuple(BATCH_IDENTITIES)
V173_BATCH_GOLDEN_SHA256 = (
    "f41c15e8273e7918b0dd6bb658eb300899eda57b8e4e7a9088644c636f8e273a"
)


class V173KnowledgeRecordTests(unittest.TestCase):
    def test_identity_schema_provenance_and_review_checklist(self):
        for canonical_name, expected in BATCH_IDENTITIES.items():
            with self.subTest(artist=canonical_name):
                record = database.get_knowledge_record(canonical_name)

                self.assertIsNotNone(record)
                self.assertIs(knowledge.validate_knowledge_record(record), record)
                self.assertEqual(record["artist_id"], expected["artist_id"])
                self.assertEqual(record["canonical_name"], canonical_name)
                self.assertEqual(record["display_name"], expected["display_name"])
                self.assertEqual(record["aliases"], expected["aliases"])
                self.assertEqual(
                    record["localized_names"],
                    expected["localized_names"],
                )
                self.assertEqual(
                    set(record["semantic"]["style_profile"]),
                    set(knowledge.STYLE_PROFILE_FIELDS),
                )
                self.assertEqual(
                    record["metadata"]["review_status"],
                    "published",
                )
                self.assertNotEqual(
                    record["metadata"]["source"],
                    "legacy_migration",
                )
                self.assertTrue(record["semantic"]["evidence"])
                self.assertTrue(
                    all(
                        item["type"] != "legacy_migration"
                        for item in record["semantic"]["evidence"]
                    )
                )
                checklist = knowledge.build_artist_review_checklist(
                    record,
                    existing_records=(
                        item
                        for item in database.KNOWLEDGE_RECORDS
                        if item["artist_id"] != record["artist_id"]
                    ),
                )
                self.assertTrue(all(checklist.values()))

    def test_names_resolve_without_alias_conflicts(self):
        artists = database.list_artists()
        self.assertEqual(len(artists), 37)
        self.assertEqual(artists, sorted(artists, key=str.casefold))

        for canonical_name, expected in BATCH_IDENTITIES.items():
            self.assertEqual(artists.count(canonical_name), 1)
            for query in expected["queries"]:
                with self.subTest(artist=canonical_name, query=query):
                    entry = database.get_artist(query)
                    self.assertIsNotNone(entry)
                    self.assertEqual(entry["canonical_name"], canonical_name)

    def test_profiles_are_complete_distinct_and_contain_no_shortcuts(self):
        profiles = {
            artist: database.get_artist(artist)["style_profile"]
            for artist in BATCH_ARTISTS
        }
        all_existing = {
            record["canonical_name"]: record["style_profile"]
            for record in database.ARTISTS
            if record["canonical_name"] not in BATCH_ARTISTS
        }

        for artist, profile in profiles.items():
            with self.subTest(artist=artist):
                self.assertEqual(
                    tuple(profile),
                    knowledge.STYLE_PROFILE_FIELDS,
                )
                self.assertTrue(all(profile.values()))
                self.assertNotEqual(profile, prompt_builder.GENERIC_STYLE_PROFILE)
                self.assertTrue(
                    all(profile != existing for existing in all_existing.values())
                )
                text = " ".join(
                    phrase for values in profile.values() for phrase in values
                ).casefold()
                self.assertNotIn("in the style of", text)
                self.assertNotIn("masterpiece", text)
                self.assertNotIn("best quality", text)

        self.assertEqual(len({repr(profile) for profile in profiles.values()}), 5)

    def test_each_record_passes_draft_reviewed_published_boundaries(self):
        for artist in BATCH_ARTISTS:
            with self.subTest(artist=artist):
                published = database.get_knowledge_record(artist)

                draft = deepcopy(published)
                draft["metadata"]["review_status"] = "draft"
                draft_loader = knowledge.KnowledgeBaseLoader((draft,))
                self.assertEqual(draft_loader.list_artists(), [])
                self.assertIsNone(draft_loader.get_knowledge_record(artist))

                reviewed = deepcopy(published)
                reviewed["metadata"]["review_status"] = "reviewed"
                reviewed_loader = knowledge.KnowledgeBaseLoader((reviewed,))
                self.assertEqual(reviewed_loader.list_artists(), [])
                self.assertIsNone(reviewed_loader.get_knowledge_record(artist))
                self.assertIsNotNone(
                    reviewed_loader.get_knowledge_record(
                        artist,
                        include_reviewed=True,
                    )
                )

                published_loader = knowledge.KnowledgeBaseLoader((published,))
                self.assertEqual(published_loader.list_artists(), [artist])
                self.assertIsNotNone(published_loader.get_artist(artist))


class V173RuntimeIntegrationTests(unittest.TestCase):
    def test_selector_provider_resolver_and_preview_integrate_every_artist(self):
        selector_artists = nodes.ArtistStyleSelector.INPUT_TYPES()["required"][
            "artist"
        ][0]
        provider = builtin_provider.BuiltinSemanticProvider()
        resolver = resolver_module.ArtistStyleResolver()

        for artist in BATCH_ARTISTS:
            with self.subTest(artist=artist):
                self.assertIn(artist, selector_artists)
                self.assertIn(artist, provider.list_artists())
                self.assertTrue(provider.supports(artist))
                profile = provider.get_profile(artist)
                self.assertEqual(profile, resolver.resolve(artist))

                text, json_text = nodes.SemanticProfilePreview().preview_profile(
                    artist
                )
                payload = json.loads(json_text)
                expected_phrase = database.get_artist(artist)["style_profile"][
                    "medium"
                ][0]
                self.assertIn(expected_phrase, text)
                self.assertEqual(payload["source"], "builtin")
                self.assertEqual(payload["generated_by"], "artist_database")
                self.assertTrue(payload["features"])
                self.assertNotIn("curated_public_source_review", json_text)
                self.assertNotIn("pixiv.net", json_text)

    def test_translator_models_detail_levels_advanced_and_prompt_merge(self):
        translator = nodes.ArtistStyleTranslator()
        advanced = nodes.ArtistStyleTranslatorAdvanced()
        merger = nodes.ArtistStylePromptMerge()

        for artist in BATCH_ARTISTS:
            for model in prompt_builder.TARGET_MODELS:
                for detail in prompt_builder.DETAIL_LEVELS:
                    with self.subTest(
                        artist=artist,
                        model=model,
                        detail=detail,
                    ):
                        standard = translator.translate_style(
                            artist,
                            model,
                            detail,
                        )
                        advanced_result = advanced.translate_style(
                            artist,
                            model,
                            detail,
                        )
                        fallback = translator.translate_style(
                            "V1.7.3 Unknown Artist",
                            model,
                            detail,
                        )
                        merged = merger.merge_prompts(
                            "portrait",
                            standard[0],
                        )

                        self.assertEqual(standard, advanced_result)
                        self.assertNotEqual(standard, fallback)
                        self.assertTrue(standard[0])
                        self.assertNotIn("in the style of", standard[0].casefold())
                        self.assertEqual(merged, (f"portrait\n\n{standard[0]}",))

    def test_all_75_batch_prompts_match_v173_baseline(self):
        rows = [
            (
                artist,
                model,
                detail,
                prompt_builder.build_prompt(artist, model, detail),
            )
            for artist in BATCH_ARTISTS
            for model in prompt_builder.TARGET_MODELS
            for detail in prompt_builder.DETAIL_LEVELS
        ]
        serialized = json.dumps(
            rows,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        self.assertEqual(len(rows), 5 * 5 * 3)
        self.assertEqual(
            hashlib.sha256(serialized).hexdigest(),
            V173_BATCH_GOLDEN_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
