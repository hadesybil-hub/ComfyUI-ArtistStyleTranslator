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
            style_engine.Feature(
                category="linework",
                value="controlled contours",
                priority=0.73,
                source="user",
                confidence=0.79,
                evidence=(),
                generated_by="user_test",
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

    def test_text_groups_categories_in_first_seen_order(self):
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
        self.assertEqual(text.count("  linework:"), 1)
        self.assertLess(text.index("  linework:"), text.index("  lighting:"))

    def test_category_preserves_original_feature_order(self):
        profile = sample_profile()
        text = preview.profile_to_text(profile)
        linework_values = [
            feature.value
            for feature in profile.features
            if feature.category == "linework"
        ]

        self.assertLess(
            text.index(linework_values[0]),
            text.index(linework_values[1]),
        )

    def test_priority_uses_two_decimal_places(self):
        text = preview.profile_to_text(sample_profile())

        self.assertIn("priority=0.40", text)
        self.assertIn("priority=0.90", text)
        self.assertIn("priority=0.73", text)
        self.assertNotIn("priority=0.400", text)

    def test_compact_text_hides_repeated_feature_metadata(self):
        text = preview.profile_to_text(sample_profile())

        self.assertIn("source: user", text)
        self.assertIn("confidence: 0.880", text)
        self.assertIn("evidence: profile observation", text)
        self.assertNotIn("source: builtin", text)
        self.assertNotIn("confidence: 0.810", text)
        self.assertNotIn("evidence: line observation", text)
        self.assertNotIn("generated_by: test_provider", text)

    def test_verbose_text_shows_complete_feature_metadata(self):
        text = preview.profile_to_text(sample_profile(), verbose=True)

        self.assertIn("source: builtin", text)
        self.assertIn("confidence: 0.810", text)
        self.assertIn("evidence: line observation", text)
        self.assertIn("generated_by: test_provider", text)
        self.assertIn("evidence: (none)", text)

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

    def test_json_is_unchanged_by_verbose_text_mode(self):
        profile = sample_profile()

        compact_json = preview.format_profile(
            profile,
            "json",
            verbose=False,
        )
        verbose_json = preview.format_profile(
            profile,
            "json",
            verbose=True,
        )

        self.assertEqual(compact_json, verbose_json)
        self.assertEqual(compact_json, preview.profile_to_json(profile))

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
