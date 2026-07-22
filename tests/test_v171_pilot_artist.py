"""Integration coverage for the V1.7.1 Homare pilot knowledge record."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import hashlib
import json
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v171_pilot_tests"
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


class HomareKnowledgeRecordTests(unittest.TestCase):
    def test_record_identity_schema_and_research_provenance(self):
        record = database.get_knowledge_record("Homare")

        self.assertIsNotNone(record)
        self.assertIs(knowledge.validate_knowledge_record(record), record)
        self.assertEqual(record["artist_id"], "homare")
        self.assertEqual(record["canonical_name"], "Homare")
        self.assertEqual(record["display_name"], "Homare")
        self.assertEqual(record["aliases"], ("homare_works",))
        self.assertEqual(record["localized_names"], {"ja": ("誉",)})
        self.assertEqual(
            record["category"],
            ("illustrator", "character_designer"),
        )
        self.assertEqual(
            set(record["semantic"]["style_profile"]),
            set(knowledge.STYLE_PROFILE_FIELDS),
        )
        self.assertEqual(record["metadata"]["review_status"], "published")
        self.assertEqual(record["semantic"]["profile_confidence"], 0.85)
        self.assertTrue(
            all(
                item["type"] != "legacy_migration"
                for item in record["semantic"]["evidence"]
            )
        )
        references = "; ".join(
            item["reference"] for item in record["semantic"]["evidence"]
        )
        self.assertGreaterEqual(references.count("blog-entry-"), 12)

    def test_canonical_alias_and_localized_names_resolve_without_conflicts(self):
        for name in (
            "Homare",
            " HOMARE ",
            "homare_works",
            "homare works",
            "誉",
        ):
            with self.subTest(name=name):
                entry = database.get_artist(name)
                self.assertIsNotNone(entry)
                self.assertEqual(entry["canonical_name"], "Homare")

        artists = database.list_artists()
        self.assertEqual(len(artists), 37)
        self.assertEqual(artists.count("Homare"), 1)
        self.assertEqual(artists, sorted(artists, key=str.casefold))

    def test_semantics_are_distinct_and_do_not_contain_prompt_shortcuts(self):
        homare = database.get_artist("Homare")["style_profile"]
        existing = (
            record["style_profile"]
            for record in database.ARTISTS
            if record["canonical_name"] != "Homare"
        )

        self.assertTrue(all(homare != profile for profile in existing))
        semantic_text = " ".join(
            phrase
            for values in homare.values()
            for phrase in values
        ).casefold()
        self.assertNotIn("homare", semantic_text)
        self.assertNotIn("誉", semantic_text)
        self.assertNotIn("in the style of", semantic_text)


class HomareRuntimeIntegrationTests(unittest.TestCase):
    def test_selector_provider_and_resolver_expose_the_published_record(self):
        selector_artists = nodes.ArtistStyleSelector.INPUT_TYPES()["required"][
            "artist"
        ][0]
        provider = builtin_provider.BuiltinSemanticProvider()
        resolver = resolver_module.ArtistStyleResolver()

        self.assertIn("Homare", selector_artists)
        self.assertIn("Homare", provider.list_artists())
        self.assertTrue(provider.supports("誉"))
        self.assertEqual(provider.get_profile("Homare"), resolver.resolve("Homare"))

    def test_preview_text_and_json_resolve_without_exposing_research_evidence(self):
        text, json_text = nodes.SemanticProfilePreview().preview_profile("Homare")
        payload = json.loads(json_text)

        self.assertIn("polished digital character illustration", text)
        self.assertEqual(payload["source"], "builtin")
        self.assertEqual(payload["generated_by"], "artist_database")
        self.assertTrue(payload["features"])
        self.assertNotIn("blog-entry-", text)
        self.assertNotIn("blog-entry-", json_text)
        self.assertNotIn("Homare", json_text)

    def test_translator_all_models_and_detail_levels_and_prompt_merge(self):
        translator = nodes.ArtistStyleTranslator()
        merger = nodes.ArtistStylePromptMerge()

        for model in prompt_builder.TARGET_MODELS:
            for detail in prompt_builder.DETAIL_LEVELS:
                with self.subTest(model=model, detail=detail):
                    prompt = translator.translate_style(
                        "Homare",
                        model,
                        detail,
                    )[0]
                    fallback = translator.translate_style(
                        "V1.7.1 Unknown Artist",
                        model,
                        detail,
                    )[0]
                    merged = merger.merge_prompts("portrait", prompt)[0]

                    self.assertTrue(prompt)
                    self.assertNotEqual(prompt, fallback)
                    self.assertNotIn("Homare", prompt)
                    self.assertNotIn("in the style of", prompt.casefold())
                    self.assertEqual(merged, f"portrait\n\n{prompt}")

    def test_direct_database_translator_path_matches_advanced_node(self):
        standard = nodes.ArtistStyleTranslator().translate_style(
            "Homare",
            "Z-Image",
            "Standard",
        )
        advanced = nodes.ArtistStyleTranslatorAdvanced().translate_style(
            "Homare",
            "Z-Image",
            "Standard",
        )

        self.assertEqual(standard, advanced)

    def test_all_homare_prompts_match_v171_baseline(self):
        rows = [
            (
                model,
                detail,
                prompt_builder.build_prompt("Homare", model, detail),
            )
            for model in prompt_builder.TARGET_MODELS
            for detail in prompt_builder.DETAIL_LEVELS
        ]
        serialized = json.dumps(
            rows,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        self.assertEqual(len(rows), 5 * 3)
        self.assertEqual(
            hashlib.sha256(serialized).hexdigest(),
            "13b7721b9ac79efd21bad3d3079dd88c305010b25447de4a5053495ddb6c0931",
        )


if __name__ == "__main__":
    unittest.main()
