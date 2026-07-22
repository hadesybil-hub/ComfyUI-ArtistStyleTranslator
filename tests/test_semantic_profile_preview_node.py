"""Integration tests for the Semantic Profile Preview ComfyUI node."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_preview_node_tests"
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
        package,
        import_module(f"{package_name}.providers"),
        import_module(f"{package_name}.profile_formatter"),
        import_module(f"{package_name}.style_engine"),
    )


package, providers, formatter, style_engine = load_project_modules()
SemanticProfilePreview = package.NODE_CLASS_MAPPINGS[
    "SemanticProfilePreview"
]


def sample_profile():
    return style_engine.SemanticStyleProfile(
        features=(
            style_engine.Feature(
                category="rendering",
                value="layered painterly rendering",
                priority=0.9,
                source="external",
                confidence=0.87,
                evidence=("preview node observation",),
                generated_by="preview_node_test",
            ),
        ),
        source="external",
        confidence=0.84,
        evidence=("mock resolver profile",),
        generated_by="mock_resolver",
    )


class MockResolver:
    def __init__(self, profile):
        self.profile = profile
        self.calls = []

    def resolve(self, artist_name):
        self.calls.append(artist_name)
        return self.profile


class SemanticProfilePreviewNodeTests(unittest.TestCase):
    def test_node_is_registered_with_display_name(self):
        self.assertIs(
            package.NODE_CLASS_MAPPINGS["SemanticProfilePreview"],
            SemanticProfilePreview,
        )
        self.assertEqual(
            package.NODE_DISPLAY_NAME_MAPPINGS["SemanticProfilePreview"],
            "Semantic Profile Preview",
        )

    def test_node_interface_exposes_string_input_and_text_json_outputs(self):
        required = SemanticProfilePreview.INPUT_TYPES()["required"]

        self.assertEqual(required["artist_name"][0], "STRING")
        self.assertEqual(required["verbose"][0], "BOOLEAN")
        self.assertFalse(required["verbose"][1]["default"])
        self.assertEqual(
            SemanticProfilePreview.RETURN_TYPES,
            ("STRING", "STRING"),
        )
        self.assertEqual(SemanticProfilePreview.RETURN_NAMES, ("text", "json"))
        self.assertEqual(SemanticProfilePreview.FUNCTION, "preview_profile")

    def test_node_integrates_resolver_and_formatter(self):
        profile = sample_profile()
        resolver = MockResolver(profile)
        node = SemanticProfilePreview(resolver=resolver)

        result = node.preview_profile("Preview Artist")

        self.assertEqual(resolver.calls, ["Preview Artist"])
        self.assertEqual(
            result,
            (
                formatter.profile_to_text(profile),
                formatter.profile_to_json(profile),
            ),
        )

    def test_verbose_changes_text_but_not_json(self):
        profile = sample_profile()
        node = SemanticProfilePreview(resolver=MockResolver(profile))

        compact_text, compact_json = node.preview_profile(
            "Preview Artist",
            False,
        )
        verbose_text, verbose_json = node.preview_profile(
            "Preview Artist",
            True,
        )

        self.assertNotIn("source: external\n", compact_text.split("features:")[1])
        self.assertIn("source: external", verbose_text.split("features:")[1])
        self.assertEqual(compact_json, verbose_json)

    def test_unknown_artist_uses_existing_resolver_fallback(self):
        text, profile_json = SemanticProfilePreview().preview_profile(
            "V1.6.4 Unknown Preview Artist"
        )
        payload = json.loads(profile_json)

        self.assertEqual(payload["source"], "builtin")
        self.assertEqual(payload["confidence"], 0.85)
        self.assertEqual(payload["generated_by"], "prompt_builder.fallback")
        self.assertEqual(
            payload["evidence"],
            ["builtin generic fallback profile"],
        )
        self.assertIn("generated_by: prompt_builder.fallback", text)

    def test_json_output_contains_resolved_profile_metadata(self):
        artist = providers.BuiltinSemanticProvider().list_artists()[0]
        _, profile_json = SemanticProfilePreview().preview_profile(artist)
        payload = json.loads(profile_json)

        self.assertEqual(payload["source"], "builtin")
        self.assertEqual(payload["generated_by"], "artist_database")
        self.assertTrue(payload["features"])
        self.assertIn("category", payload["features"][0])
        self.assertIn("evidence", payload["features"][0])

    def test_text_output_contains_profile_and_feature_content(self):
        artist = providers.BuiltinSemanticProvider().list_artists()[0]
        text, _ = SemanticProfilePreview().preview_profile(artist)
        profile = providers.BuiltinSemanticProvider().get_profile(artist)

        self.assertTrue(text.startswith("Semantic Style Profile\n"))
        self.assertIn("source: builtin", text)
        self.assertIn("features:", text)
        self.assertIn(profile.features[0].category, text)
        self.assertIn(profile.features[0].value, text)


if __name__ == "__main__":
    unittest.main()
