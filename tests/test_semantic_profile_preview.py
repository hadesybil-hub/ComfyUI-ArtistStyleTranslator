"""Tests for read-only SemanticStyleProfile preview formatting."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_preview_tests"
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
        import_module(f"{package_name}.profile_formatter"),
        import_module(f"{package_name}.style_engine"),
    )


preview, style_engine = load_project_modules()


def sample_profile():
    return style_engine.SemanticStyleProfile(
        features=(
            style_engine.Feature(
                category="linework",
                value="精细线条",
                priority=0.4,
                source="builtin",
                confidence=0.81,
                evidence=("line observation",),
                generated_by="test_provider",
            ),
            style_engine.Feature(
                category="lighting",
                value="soft illumination",
                priority=0.9,
                source="external",
                confidence=0.93,
                evidence=("light observation", "secondary source"),
                generated_by="external_test",
            ),
        ),
        source="user",
        confidence=0.88,
        evidence=("profile observation",),
        generated_by="preview_test",
    )


class SemanticProfilePreviewTests(unittest.TestCase):
    def test_dict_preserves_profile_and_feature_metadata(self):
        result = preview.profile_to_dict(sample_profile())

        self.assertEqual(result["source"], "user")
        self.assertEqual(result["confidence"], 0.88)
        self.assertEqual(result["evidence"], ["profile observation"])
        self.assertEqual(result["generated_by"], "preview_test")
        self.assertEqual(result["features"][0]["category"], "linework")
        self.assertEqual(result["features"][0]["confidence"], 0.81)
        self.assertEqual(
            result["features"][1]["evidence"],
            ["light observation", "secondary source"],
        )

    def test_outputs_preserve_feature_order_without_reranking(self):
        profile = sample_profile()
        mapping = preview.profile_to_dict(profile)
        text = preview.profile_to_text(profile)

        self.assertEqual(
            [item["category"] for item in mapping["features"]],
            [feature.category for feature in profile.features],
        )
        self.assertIn("source: user", text)
        self.assertIn("confidence: 0.880", text)
        self.assertIn("generated_by: preview_test", text)
        self.assertIn("evidence: profile observation", text)
        self.assertIn("priority=0.400", text)
        self.assertIn("evidence: line observation", text)
        self.assertLess(text.index("[linework]"), text.index("[lighting]"))

    def test_json_is_deterministic_unicode_and_parseable(self):
        profile = sample_profile()
        first = preview.profile_to_json(profile)
        second = preview.profile_to_json(profile)

        self.assertEqual(first, second)
        self.assertIn("精细线条", first)
        self.assertEqual(
            json.loads(first),
            preview.profile_to_dict(profile),
        )

    def test_invalid_input_is_rejected(self):
        formatters = (
            preview.profile_to_dict,
            preview.profile_to_json,
            preview.profile_to_text,
        )
        for formatter in formatters:
            with self.subTest(formatter=formatter.__name__):
                with self.assertRaises(TypeError):
                    formatter({})


if __name__ == "__main__":
    unittest.main()
