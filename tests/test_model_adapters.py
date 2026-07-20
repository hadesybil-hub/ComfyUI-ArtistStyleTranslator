"""Tests for deterministic model-specific output adapters."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_package():
    root = Path(__file__).resolve().parents[1]
    name = "artist_style_translator_adapter_tests"
    spec = spec_from_file_location(
        name, root / "__init__.py", submodule_search_locations=[str(root)]
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load project package")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return name


PACKAGE_NAME = load_package()
adapters = sys.modules[f"{PACKAGE_NAME}.model_adapters"]
database = sys.modules[f"{PACKAGE_NAME}.artist_database"]
style_engine = sys.modules[f"{PACKAGE_NAME}.style_engine"]


class ModelAdapterTests(unittest.TestCase):
    def setUp(self):
        self.profile = database.get_artist("WLOP")["style_profile"]

    def test_supported_models_and_normalization(self):
        self.assertEqual(
            adapters.SUPPORTED_MODELS,
            ("Generic", "Z-Image", "FLUX", "Qwen-Image", "Krea"),
        )
        self.assertEqual(adapters.normalize_target_model("flux"), "FLUX")
        self.assertEqual(adapters.normalize_target_model("unknown"), "Z-Image")

    def test_every_model_returns_nonempty_text(self):
        for model in adapters.SUPPORTED_MODELS:
            value = adapters.adapt_style_profile(self.profile, model, "Standard")
            self.assertIsInstance(value, str)
            self.assertTrue(value.strip())

    def test_models_use_at_least_three_text_structures(self):
        values = {
            adapters.adapt_style_profile(self.profile, model, "Standard")
            for model in adapters.SUPPORTED_MODELS
        }
        self.assertGreaterEqual(len(values), 3)
        self.assertIn(".", adapters.adapt_style_profile(self.profile, "FLUX", "Standard"))
        self.assertNotIn(".", adapters.adapt_style_profile(self.profile, "Krea", "Short"))

    def test_flux_uses_complete_sentences(self):
        value = adapters.adapt_style_profile(self.profile, "FLUX", "Detailed")
        sentences = [part for part in value.split(". ") if part.strip()]
        self.assertGreaterEqual(len(sentences), 2)
        self.assertTrue(value.endswith("."))

    def test_krea_short_is_shorter_than_detailed_flux(self):
        krea = adapters.adapt_style_profile(self.profile, "Krea", "Short")
        flux = adapters.adapt_style_profile(self.profile, "FLUX", "Detailed")
        self.assertLess(len(krea), len(flux))
        self.assertIn("digital painting", krea)

    def test_adapter_accepts_prompt_units_without_database_access(self):
        semantic = style_engine.semanticize_style_profile(
            self.profile,
            source="builtin",
            confidence=0.91,
            generated_by="test",
        )
        units = style_engine.to_prompt_units(semantic)[:8]
        output = adapters.adapt_style_profile(units, "Z-Image", "Short")
        self.assertTrue(output)
        self.assertTrue(all(unit.confidence == 0.91 for unit in units))


if __name__ == "__main__":
    unittest.main()
