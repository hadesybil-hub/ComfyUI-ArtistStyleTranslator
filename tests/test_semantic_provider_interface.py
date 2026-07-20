"""Tests for the V1.5.1 provider-neutral semantic interface."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import inspect
import json
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_provider_interface_tests"
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
        import_module(f"{package_name}.artist_database"),
    )


providers, style_engine, artist_database = load_project_modules()


def structured_data(**overrides):
    data = {
        "artist": "external artist identifier",
        "source": "user",
        "generated_by": "mock_external_llm",
        "confidence": 0.87,
        "evidence": ["structured observation"],
        "features": [
            {
                "category": "rendering",
                "value": "layered painterly rendering",
                "priority": 0.9,
                "confidence": 0.91,
            },
            {
                "category": "lighting",
                "value": "soft directional lighting",
                "source": "web",
                "generated_by": "curated_observation",
                "evidence": ["feature-specific evidence"],
            },
        ],
    }
    data.update(overrides)
    return data


class MockExternalProvider(providers.SemanticProvider):
    def get_profile(self, artist_name, external_data=None):
        if external_data is None:
            raise providers.SemanticProviderError("mock data is required")
        return providers.semantic_profile_from_external_data(
            external_data,
            source="user",
            generated_by="mock_provider",
        )


class SemanticProviderInterfaceTests(unittest.TestCase):
    def test_base_provider_interface_imports_and_is_abstract(self):
        self.assertTrue(inspect.isabstract(providers.SemanticProvider))
        with self.assertRaises(TypeError):
            providers.SemanticProvider()

    def test_mock_external_provider_creates_valid_profile(self):
        result = MockExternalProvider().get_profile("unknown", structured_data())
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertTrue(result.features)
        self.assertTrue(all(isinstance(item, style_engine.Feature) for item in result.features))

    def test_provenance_metadata_is_preserved(self):
        result = providers.ExternalSemanticProvider(
            source="ollama",
            generated_by="external_tool",
        ).get_profile("unknown", structured_data())
        self.assertEqual(result.source, "user")
        self.assertEqual(result.generated_by, "mock_external_llm")
        self.assertEqual(result.confidence, 0.87)
        self.assertEqual(result.evidence, ("structured observation",))
        rendering = next(item for item in result.features if item.category == "rendering")
        lighting = next(item for item in result.features if item.category == "lighting")
        self.assertEqual(rendering.source, "user")
        self.assertEqual(rendering.generated_by, "mock_external_llm")
        self.assertEqual(rendering.evidence, ("structured observation",))
        self.assertEqual(lighting.source, "web")
        self.assertEqual(lighting.generated_by, "curated_observation")
        self.assertEqual(lighting.evidence, ("feature-specific evidence",))

    def test_reserved_sources_are_compatible(self):
        minimal = {"features": [{"category": "color", "value": "muted palette"}]}
        for source in ("builtin", "ollama", "web", "user"):
            with self.subTest(source=source):
                result = providers.ExternalSemanticProvider(
                    source=source,
                    generated_by="test",
                ).get_profile("unknown", minimal)
                self.assertEqual(result.source, source)
                self.assertEqual(result.features[0].source, source)

    def test_invalid_external_data_fails_safely(self):
        provider = providers.ExternalSemanticProvider(source="user")
        invalid_values = (
            "{not json",
            {},
            {"features": []},
            {"features": [{"category": "rendering"}]},
            {"features": [{"category": "rendering", "value": "painted", "confidence": 2}]},
        )
        for invalid in invalid_values:
            with self.subTest(invalid=invalid):
                with self.assertRaises(providers.ExternalDataValidationError):
                    provider.get_profile("unknown", invalid)
                self.assertIsNone(provider.try_get_profile("unknown", invalid))

    def test_json_string_is_accepted(self):
        result = providers.ExternalSemanticProvider(source="user").get_profile(
            "unknown",
            json.dumps(structured_data()),
        )
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)

    def test_builtin_provider_matches_existing_semantic_conversion(self):
        entry = artist_database.get_artist("WLOP")
        expected = style_engine.semanticize_style_profile(
            entry["style_profile"],
            source="builtin",
            confidence=0.95,
            evidence=("builtin structured style profile",),
            generated_by="artist_database",
        )
        provider = providers.BuiltinSemanticProvider()
        result = provider.get_profile("  wlop  ")
        self.assertEqual(result, expected)
        self.assertEqual(result.source, "builtin")
        self.assertEqual(result.generated_by, "artist_database")
        self.assertIsNone(provider.try_get_profile("not in database"))

    def test_adapter_returns_semantics_not_final_prompt(self):
        result = providers.semantic_profile_from_external_data(structured_data())
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertFalse(isinstance(result, str))


if __name__ == "__main__":
    unittest.main()
