"""Tests for V1.6.1 builtin/external/fallback resolution priority."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_resolver_tests"
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
        import_module(f"{package_name}.resolver"),
        import_module(f"{package_name}.providers"),
        import_module(f"{package_name}.prompt_builder"),
        import_module(f"{package_name}.style_engine"),
    )


resolver, providers, prompt_builder, style_engine = load_project_modules()


def valid_external_profile():
    return {
        "artist": "unknown artist",
        "confidence": 0.88,
        "evidence": "mock external observation",
        "features": [
            {
                "category": "rendering",
                "value": "layered painterly rendering",
                "priority": 0.9,
                "confidence": 0.91,
            },
            {
                "category": "lighting",
                "value": "soft directional illumination",
                "priority": 0.8,
                "confidence": 0.86,
            },
        ],
    }


class MockExternalProvider:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_profile(self, artist_name):
        self.calls.append(artist_name)
        return self.result


class ArtistStyleResolverTests(unittest.TestCase):
    def test_builtin_artist_wins_over_external_source(self):
        external = MockExternalProvider(valid_external_profile())
        result = resolver.ArtistStyleResolver(external).resolve("WLOP")
        expected = providers.BuiltinSemanticProvider().get_profile("WLOP")

        self.assertEqual(result, expected)
        self.assertEqual(result.source, "builtin")
        self.assertEqual(external.calls, [])

    def test_unknown_artist_resolves_through_mock_external_provider(self):
        external = MockExternalProvider(valid_external_profile())
        result = resolver.resolve_artist_style("  New Artist  ", external)

        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertEqual(result.source, "external")
        self.assertEqual(result.generated_by, "external")
        self.assertEqual(result.confidence, 0.88)
        self.assertEqual(external.calls, ["New Artist"])
        self.assertEqual(len(result.features), 2)

    def test_invalid_external_profile_is_rejected(self):
        external = MockExternalProvider(
            {"features": [{"category": "rendering"}]}
        )
        with self.assertRaises(providers.ExternalProfileAdapterError):
            resolver.ArtistStyleResolver(external).resolve("Unknown Artist")

    def test_fallback_behavior_is_unchanged_without_external_result(self):
        expected = prompt_builder.build_semantic_profile_for_artist(
            "Unknown Artist",
            "Standard",
        ).semantic_profile

        without_provider = resolver.resolve_artist_style("Unknown Artist")
        empty_external = MockExternalProvider(None)
        without_external_result = resolver.resolve_artist_style(
            "Unknown Artist",
            empty_external,
        )

        self.assertEqual(without_provider, expected)
        self.assertEqual(without_external_result, expected)
        self.assertEqual(without_provider.source, "builtin")
        self.assertEqual(
            without_provider.generated_by,
            "prompt_builder.fallback",
        )


if __name__ == "__main__":
    unittest.main()
