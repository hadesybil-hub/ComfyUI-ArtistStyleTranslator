"""Mock-only tests for the dependency-free Ollama provider foundation."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys
import unittest


def load_provider_package():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_ollama_provider_tests"
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
    providers = import_module(f"{package_name}.providers")
    style_engine = import_module(f"{package_name}.style_engine")
    return providers, style_engine


providers, style_engine = load_provider_package()


def valid_mock_response():
    return json.dumps(
        {
            "artist": "unknown_artist",
            "confidence": 0.86,
            "evidence": ["mock semantic analysis"],
            "features": [
                {
                    "category": "rendering",
                    "value": "layered painterly rendering",
                    "priority": 0.91,
                    "confidence": 0.88,
                },
                {
                    "category": "composition",
                    "value": "wide cinematic framing",
                    "priority": 0.84,
                },
                {
                    "category": "lighting",
                    "value": "volumetric directional light",
                    "priority": 0.87,
                    "evidence": ["mock lighting observation"],
                },
                {
                    "category": "atmosphere",
                    "value": "soft atmospheric haze",
                    "priority": 0.79,
                },
            ],
        }
    )


class OllamaProviderTests(unittest.TestCase):
    def test_provider_import_and_schema_are_available(self):
        self.assertTrue(hasattr(providers, "OllamaProvider"))
        self.assertEqual(providers.OLLAMA_RESPONSE_SCHEMA["type"], "object")
        self.assertIn("features", providers.OLLAMA_RESPONSE_SCHEMA["required"])

    def test_mock_response_creates_semantic_style_profile(self):
        received_names = []

        def mock_loader(artist_name):
            received_names.append(artist_name)
            return valid_mock_response()

        provider = providers.OllamaProvider(mock_loader)
        result = provider.get_semantic_profile("  unknown_artist  ")
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertEqual(received_names, ["unknown_artist"])
        self.assertEqual(len(result.features), 4)
        self.assertTrue(all(isinstance(item, style_engine.Feature) for item in result.features))

    def test_source_confidence_evidence_and_generator_are_preserved(self):
        result = providers.OllamaProvider(
            lambda _: valid_mock_response()
        ).get_semantic_profile("demo")
        self.assertEqual(result.source, "ollama")
        self.assertEqual(result.generated_by, "ollama")
        self.assertEqual(result.confidence, 0.86)
        self.assertEqual(result.evidence, ("mock semantic analysis",))
        for feature in result.features:
            self.assertEqual(feature.source, "ollama")
            self.assertEqual(feature.generated_by, "ollama")
            self.assertGreater(feature.confidence, 0.0)
            self.assertTrue(feature.evidence)

    def test_invalid_json_is_a_controlled_failure(self):
        provider = providers.OllamaProvider(lambda _: "{not valid json")
        with self.assertRaises(providers.OllamaResponseValidationError):
            provider.get_semantic_profile("demo")
        self.assertIsNone(provider.try_get_semantic_profile("demo"))

    def test_invalid_schema_is_rejected(self):
        invalid_responses = (
            {},
            {"features": []},
            {"features": [{"category": "rendering"}]},
            {"features": [{"category": "rendering", "value": ""}]},
            {
                "features": [
                    {
                        "category": "rendering",
                        "value": "painted",
                        "confidence": 2.0,
                    }
                ]
            },
        )
        for response in invalid_responses:
            with self.subTest(response=response):
                with self.assertRaises(providers.OllamaResponseValidationError):
                    providers.validate_ollama_response(response)

    def test_no_loader_fails_without_network_activity(self):
        provider = providers.OllamaProvider()
        with self.assertRaises(providers.OllamaProviderUnavailableError):
            provider.get_semantic_profile("demo")
        self.assertIsNone(provider.try_get_semantic_profile("demo"))


if __name__ == "__main__":
    unittest.main()
