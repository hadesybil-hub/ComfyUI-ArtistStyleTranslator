"""Tests for the V1.6.2 Provider Extension Contract."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import inspect
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_provider_contract_tests"
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
        import_module(f"{package_name}.resolver"),
        import_module(f"{package_name}.artist_database"),
    )


providers, style_engine, resolver, artist_database = load_project_modules()


def semantic_profile(source="user", generated_by="mock_provider"):
    evidence = ("direct visual observation",)
    return style_engine.SemanticStyleProfile(
        features=(
            style_engine.Feature(
                category="rendering",
                value="layered painterly rendering",
                priority=0.9,
                source=source,
                confidence=0.91,
                evidence=evidence,
                generated_by=generated_by,
            ),
        ),
        source=source,
        confidence=0.87,
        evidence=evidence,
        generated_by=generated_by,
    )


class MockProvider(providers.ProviderExtensionContract):
    provider_name = "mock-semantic-provider"
    provider_version = "1.6.2-test"
    description = "In-memory provider used by contract tests."
    priority = 25

    def __init__(self, result, *, supported=True, artists=None):
        self.result = result
        self.supported = supported
        self.artists = list(artists or [])
        self.calls = []
        self.support_calls = []

    def supports(self, artist_name):
        self.support_calls.append(artist_name)
        return self.supported

    def get_profile(self, artist_name):
        self.calls.append(artist_name)
        return self.result

    def list_artists(self):
        return list(self.artists)


class LegacySemanticProvider(providers.SemanticProvider):
    """Old get_profile()-only implementation using Contract defaults."""

    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_profile(self, artist_name, external_data=None):
        self.calls.append((artist_name, external_data))
        return self.result


def external_profile_data():
    return {
        "artist": "Legacy Artist",
        "confidence": 0.86,
        "evidence": "legacy provider observation",
        "features": [
            {
                "category": "rendering",
                "value": "layered painterly rendering",
                "confidence": 0.88,
            }
        ],
    }


class ProviderContractTests(unittest.TestCase):
    def test_contract_is_abstract(self):
        self.assertTrue(inspect.isabstract(providers.ProviderExtensionContract))
        with self.assertRaises(TypeError):
            providers.ProviderExtensionContract()

    def test_provider_information_fields_are_available(self):
        provider = MockProvider(semantic_profile())
        self.assertEqual(provider.provider_name, "mock-semantic-provider")
        self.assertEqual(provider.provider_version, "1.6.2-test")
        self.assertTrue(provider.description)
        self.assertEqual(provider.priority, 25)

    def test_get_profile_is_the_authoritative_query(self):
        expected = semantic_profile()
        provider = MockProvider(expected)

        result = provider.resolve("  Example Artist  ")

        self.assertIs(result, expected)
        self.assertEqual(provider.support_calls, ["Example Artist"])
        self.assertEqual(provider.calls, ["Example Artist"])

    def test_supports_can_skip_profile_lookup(self):
        provider = MockProvider(semantic_profile(), supported=False)

        result = providers.resolve_provider(provider, "Unknown Artist")

        self.assertIsNone(result)
        self.assertEqual(provider.support_calls, ["Unknown Artist"])
        self.assertEqual(provider.calls, [])

    def test_list_artists_returns_provider_discovery_data(self):
        provider = MockProvider(
            semantic_profile(),
            artists=["WLOP", "Ilya Kuvshinov"],
        )
        self.assertEqual(
            provider.list_artists(),
            ["WLOP", "Ilya Kuvshinov"],
        )

    def test_builtin_provider_contract_compliance_and_discovery(self):
        provider = providers.BuiltinSemanticProvider()

        self.assertIsInstance(
            provider,
            providers.ProviderExtensionContract,
        )
        self.assertEqual(provider.provider_name, "builtin")
        self.assertEqual(provider.provider_version, "1.6.2")
        self.assertTrue(provider.description)
        self.assertIsInstance(provider.priority, int)
        self.assertTrue(provider.supports("WLOP"))
        self.assertFalse(provider.supports("Unknown Contract Artist"))
        self.assertEqual(
            provider.list_artists(),
            artist_database.list_artists(),
        )
        self.assertIsInstance(
            provider.get_profile("WLOP"),
            style_engine.SemanticStyleProfile,
        )

    def test_external_provider_contract_compliance_and_discovery(self):
        provider = providers.ExternalSemanticProvider(
            source="user",
            generated_by="contract_test",
        )

        self.assertIsInstance(
            provider,
            providers.ProviderExtensionContract,
        )
        self.assertEqual(provider.provider_name, "external")
        self.assertEqual(provider.provider_version, "1.6.2")
        self.assertTrue(provider.description)
        self.assertIsInstance(provider.priority, int)
        self.assertTrue(provider.supports("External Artist"))
        self.assertEqual(provider.list_artists(), [])
        self.assertLess(
            provider.priority,
            providers.BuiltinSemanticProvider.priority,
        )

        result = provider.get_profile(
            "External Artist",
            external_profile_data(),
        )
        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertIsNone(
            providers.resolve_provider(provider, "External Artist")
        )

    def test_mock_provider_implementation(self):
        expected = semantic_profile()
        provider = MockProvider(expected)

        result = providers.resolve_provider(provider, "  Example Artist  ")

        self.assertIs(result, expected)
        self.assertEqual(provider.calls, ["Example Artist"])

    def test_resolver_accepts_extension_contract_provider(self):
        expected = semantic_profile()
        provider = MockProvider(expected)

        result = resolver.resolve_artist_style(
            "  Contract-only Artist  ",
            provider,
        )

        self.assertIs(result, expected)
        self.assertEqual(provider.calls, ["Contract-only Artist"])

    def test_legacy_semantic_provider_get_profile_remains_compatible(self):
        expected = semantic_profile()
        provider = LegacySemanticProvider(expected)

        result = providers.resolve_provider(provider, "Legacy Artist")

        self.assertIs(result, expected)
        self.assertEqual(provider.calls, [("Legacy Artist", None)])
        self.assertTrue(provider.supports("Legacy Artist"))
        self.assertEqual(provider.list_artists(), [])

    def test_legacy_resolver_injection_paths_remain_compatible(self):
        class GetProfileProvider:
            def get_profile(self, artist_name):
                return external_profile_data()

        def callable_provider(artist_name):
            return external_profile_data()

        for provider in (GetProfileProvider(), callable_provider):
            with self.subTest(provider=provider):
                result = resolver.resolve_artist_style(
                    "Legacy Contract Artist",
                    provider,
                )
                self.assertEqual(result.source, "external")
                self.assertEqual(result.generated_by, "external")

    def test_none_means_no_provider_match(self):
        self.assertIsNone(
            providers.resolve_provider(MockProvider(None), "Unknown Artist")
        )
        with self.assertRaises(providers.ProviderOutputValidationError):
            providers.validate_provider_output(None)

    def test_invalid_provider_outputs_are_rejected(self):
        invalid_results = ("prompt text", {}, object())
        for result in invalid_results:
            with self.subTest(result=result):
                with self.assertRaises(
                    providers.ProviderOutputValidationError
                ):
                    providers.resolve_provider(
                        MockProvider(result),
                        "Example Artist",
                    )

    def test_invalid_feature_structure_is_rejected(self):
        profile = semantic_profile()
        object.__setattr__(profile, "features", ("not a Feature",))
        with self.assertRaises(providers.ProviderOutputValidationError):
            providers.resolve_provider(MockProvider(profile), "Example Artist")

    def test_missing_required_metadata_is_rejected(self):
        mutations = (
            ("source", ""),
            ("confidence", float("nan")),
            ("evidence", ()),
            ("generated_by", ""),
        )
        for field_name, value in mutations:
            with self.subTest(field_name=field_name):
                profile = semantic_profile()
                object.__setattr__(profile, field_name, value)
                with self.assertRaises(
                    providers.ProviderOutputValidationError
                ):
                    providers.resolve_provider(
                        MockProvider(profile),
                        "Example Artist",
                    )

    def test_feature_metadata_is_required(self):
        profile = semantic_profile()
        feature = profile.features[0]
        object.__setattr__(feature, "evidence", ())
        with self.assertRaises(providers.ProviderOutputValidationError):
            providers.validate_provider_output(profile)

    def test_builtin_provider_compatibility(self):
        provider = providers.BuiltinSemanticProvider()
        result = providers.resolve_provider(provider, "  WLOP  ")

        self.assertIsInstance(result, style_engine.SemanticStyleProfile)
        self.assertEqual(result, provider.get_profile("WLOP"))
        self.assertEqual(result.source, "builtin")
        self.assertEqual(result.generated_by, "artist_database")
        self.assertIsNone(
            providers.resolve_provider(provider, "Unknown Artist")
        )

    def test_external_profile_adapter_compatibility(self):
        result = providers.adapt_external_profile(
            {
                "artist": "Example Artist",
                "confidence": 0.84,
                "evidence": "external profile observation",
                "features": [
                    {
                        "category": "lighting",
                        "value": "soft directional lighting",
                        "priority": 0.8,
                        "confidence": 0.82,
                    }
                ],
            }
        )

        self.assertIs(providers.validate_provider_output(result), result)
        self.assertEqual(result.source, "external")
        self.assertEqual(result.generated_by, "external")

    def test_metadata_is_preserved(self):
        expected = semantic_profile(source="web", generated_by="curator_v1")
        result = providers.resolve_provider(
            MockProvider(expected),
            "Example Artist",
        )

        self.assertIs(result, expected)
        self.assertEqual(result.source, "web")
        self.assertEqual(result.confidence, 0.87)
        self.assertEqual(result.evidence, ("direct visual observation",))
        self.assertEqual(result.generated_by, "curator_v1")
        self.assertEqual(result.features[0].source, "web")
        self.assertEqual(result.features[0].confidence, 0.91)
        self.assertEqual(
            result.features[0].evidence,
            ("direct visual observation",),
        )
        self.assertEqual(result.features[0].generated_by, "curator_v1")


if __name__ == "__main__":
    unittest.main()
