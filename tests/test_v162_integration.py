"""End-to-end integration coverage for the complete V1.6.2 feature set."""

from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v162_integration_tests"
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
        import_module(f"{package_name}.resolver"),
        import_module(f"{package_name}.style_engine"),
    )


package, providers, resolver, style_engine = load_project_modules()


def external_profile_data():
    return {
        "artist": "V1.6.2 External Integration Artist",
        "confidence": 0.87,
        "evidence": "integration test semantic observation",
        "features": [
            {
                "category": "rendering",
                "value": "layered painterly rendering",
                "priority": 0.9,
                "confidence": 0.89,
            },
            {
                "category": "lighting",
                "value": "soft directional illumination",
                "priority": 0.8,
                "confidence": 0.85,
            },
        ],
    }


class LegacyGetProfileProvider:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_profile(self, artist_name):
        self.calls.append(artist_name)
        return self.result


class V162IntegrationTests(unittest.TestCase):
    def setUp(self):
        mappings = package.NODE_CLASS_MAPPINGS
        self.selector = mappings["ArtistStyleSelector"]()
        self.translator = mappings["ArtistStyleTranslator"]()
        self.merge = mappings["ArtistStylePromptMerge"]()

    @staticmethod
    def _first_discovered_artist():
        selector_class = package.NODE_CLASS_MAPPINGS["ArtistStyleSelector"]
        return selector_class.INPUT_TYPES()["required"]["artist"][0][0]

    def test_selector_output_connects_to_translator(self):
        selector_class = type(self.selector)
        translator_class = type(self.translator)
        artist = self._first_discovered_artist()

        selected = self.selector.select_artist(artist)
        translated = self.translator.translate_style(
            selected[0],
            "Z-Image",
            "Standard",
        )

        self.assertEqual(selector_class.RETURN_TYPES, ("STRING",))
        self.assertEqual(
            translator_class.INPUT_TYPES()["required"]["artist_name"][0],
            selector_class.RETURN_TYPES[0],
        )
        self.assertIsInstance(selected[0], str)
        self.assertIsInstance(translated, tuple)
        self.assertEqual(len(translated), 1)
        self.assertIsInstance(translated[0], str)
        self.assertTrue(translated[0])

    def test_direct_and_selector_translator_inputs_are_compatible(self):
        artist = self._first_discovered_artist()
        selected_artist = self.selector.select_artist(artist)[0]

        direct = self.translator.translate_style(
            artist,
            "FLUX",
            "Detailed",
        )
        selected = self.translator.translate_style(
            selected_artist,
            "FLUX",
            "Detailed",
        )

        self.assertEqual(direct, selected)
        self.assertIsInstance(direct, tuple)
        self.assertEqual(len(direct), 1)

    def test_translator_output_connects_to_prompt_merge(self):
        artist = self._first_discovered_artist()
        translated = self.translator.translate_style(
            self.selector.select_artist(artist)[0],
            "Z-Image",
            "Standard",
        )

        merged = self.merge.merge_prompts(
            "a character portrait",
            translated[0],
        )

        self.assertEqual(
            merged,
            (f"a character portrait\n\n{translated[0]}",),
        )
        self.assertEqual(type(self.merge).RETURN_TYPES, ("STRING",))

    def test_builtin_and_external_provider_contract_chain(self):
        builtin = providers.BuiltinSemanticProvider()
        artists = builtin.list_artists()

        self.assertTrue(artists)
        self.assertTrue(builtin.supports(artists[0]))
        builtin_profile = builtin.get_profile(artists[0])
        self.assertIsInstance(
            builtin_profile,
            style_engine.SemanticStyleProfile,
        )
        self.assertEqual(builtin_profile.source, "builtin")

        external = providers.ExternalSemanticProvider(
            source="user",
            generated_by="v162_integration_test",
        )
        self.assertEqual(external.list_artists(), [])
        self.assertTrue(external.supports("External Integration Artist"))
        external_profile = external.get_profile(
            "External Integration Artist",
            external_profile_data(),
        )
        self.assertIsInstance(
            external_profile,
            style_engine.SemanticStyleProfile,
        )
        self.assertIsNone(
            providers.resolve_provider(
                external,
                "External Integration Artist",
            )
        )

    def test_resolver_preserves_builtin_external_fallback_order(self):
        builtin_artist = providers.BuiltinSemanticProvider().list_artists()[0]
        external = LegacyGetProfileProvider(external_profile_data())
        builtin_result = resolver.ArtistStyleResolver(external).resolve(
            builtin_artist
        )

        self.assertEqual(builtin_result.source, "builtin")
        self.assertEqual(external.calls, [])

        external_name = "V1.6.2 External-only Integration Artist"
        external_result = resolver.ArtistStyleResolver(external).resolve(
            external_name
        )
        self.assertEqual(external_result.source, "external")
        self.assertEqual(external.calls, [external_name])

        missing = LegacyGetProfileProvider(None)
        fallback = resolver.ArtistStyleResolver(missing).resolve(
            "V1.6.2 Missing Integration Artist"
        )
        self.assertEqual(missing.calls, ["V1.6.2 Missing Integration Artist"])
        self.assertEqual(fallback.source, "builtin")
        self.assertEqual(fallback.generated_by, "prompt_builder.fallback")

    def test_resolver_keeps_legacy_callable_and_get_profile_paths(self):
        def callable_provider(artist_name):
            return external_profile_data()

        providers_to_test = (
            callable_provider,
            LegacyGetProfileProvider(external_profile_data()),
        )
        for injected_provider in providers_to_test:
            with self.subTest(provider=injected_provider):
                result = resolver.ArtistStyleResolver(
                    injected_provider
                ).resolve("V1.6.2 Legacy Integration Artist")
                self.assertEqual(result.source, "external")
                self.assertEqual(result.generated_by, "external")


if __name__ == "__main__":
    unittest.main()
