"""Tests for the V1.6 external semantic profile adapter."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_external_profile_tests"
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
        import_module(f"{package_name}.providers"),
        import_module(f"{package_name}.style_engine"),
    )


providers, style_engine = load_project_modules()


def valid_external_profile():
    return {
        "artist": "unknown_artist",
        "confidence": 0.84,
        "evidence": "external profile observation",
        "features": [
            {
                "category": "rendering",
                "value": "painterly rendering",
                "priority": 0.9,
                "confidence": 0.93,
                "evidence": "observed brush texture",
                "generated_by": "external",
            },
            {
                "category": "lighting",
                "value": "soft directional lighting",
                "priority": 0.75,
            },
        ],
    }


class ExternalProfileAdapterTests(unittest.TestCase):
    def test_valid_external_profile_conversion(self):
        result = providers.adapt_external_profile(valid_external_profile())
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertEqual(len(result.features), 2)
        self.assertEqual(result.features[0].category, "rendering")
        self.assertEqual(result.features[0].value, "painterly rendering")

    def test_invalid_schema_is_rejected_with_controlled_failure(self):
        invalid_profiles = (
            {"features": [{"value": "painted"}]},
            {"features": [{"category": "rendering"}]},
            {
                "features": [
                    {
                        "category": "rendering",
                        "value": "painted",
                        "confidence": 1.5,
                    }
                ]
            },
            {"features": "not a feature list"},
            None,
        )
        for profile in invalid_profiles:
            with self.subTest(profile=profile):
                with self.assertRaises(providers.ExternalProfileAdapterError):
                    providers.adapt_external_profile(profile)

    def test_metadata_and_provenance_are_preserved_as_required(self):
        data = valid_external_profile()
        data["source"] = "user"
        data["generated_by"] = "future_llm"
        data["features"][0]["source"] = "web"
        data["features"][0]["generated_by"] = "future_llm"

        result = providers.adapt_external_profile(data)
        self.assertEqual(result.source, "external")
        self.assertEqual(result.generated_by, "external")
        self.assertEqual(result.confidence, 0.84)
        self.assertEqual(result.evidence, ("external profile observation",))

        rendering = next(
            item for item in result.features if item.category == "rendering"
        )
        lighting = next(
            item for item in result.features if item.category == "lighting"
        )
        self.assertEqual(rendering.source, "external")
        self.assertEqual(rendering.generated_by, "external")
        self.assertEqual(rendering.confidence, 0.93)
        self.assertEqual(rendering.evidence, ("observed brush texture",))
        self.assertEqual(lighting.source, "external")
        self.assertEqual(lighting.generated_by, "external")
        self.assertEqual(
            lighting.evidence,
            ("external profile observation",),
        )

    def test_empty_feature_list_is_rejected(self):
        with self.assertRaises(providers.ExternalProfileAdapterError):
            providers.adapt_external_profile({"features": []})

    def test_adapter_facade_uses_same_conversion(self):
        direct = providers.adapt_external_profile(valid_external_profile())
        facade = providers.ExternalProfileAdapter.convert(
            valid_external_profile()
        )
        self.assertEqual(facade, direct)


if __name__ == "__main__":
    unittest.main()
