"""Tests for the provider-neutral semantic style engine."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_style_engine():
    path = Path(__file__).resolve().parents[1] / "style_engine.py"
    name = "artist_style_translator_style_engine_tests"
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load style engine")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


engine = load_style_engine()


class StyleEngineTests(unittest.TestCase):
    def test_feature_creation_and_metadata(self):
        feature = engine.Feature(
            category="linework",
            value="clean contours",
            priority=0.9,
            source="builtin",
            confidence=0.85,
            evidence=("structured field",),
            generated_by="unit-test",
        )
        self.assertEqual(feature.category, "linework")
        self.assertEqual(feature.value, "clean contours")
        self.assertEqual(feature.priority, 0.9)
        self.assertEqual(feature.source, "builtin")
        self.assertEqual(feature.confidence, 0.85)
        self.assertEqual(feature.evidence, ("structured field",))
        self.assertEqual(feature.generated_by, "unit-test")

    def test_future_sources_are_reserved_without_provider_calls(self):
        self.assertEqual(
            engine.SUPPORTED_SOURCES,
            ("builtin", "ollama", "web", "user"),
        )
        for source in engine.SUPPORTED_SOURCES:
            profile = engine.semanticize_style_profile(
                {"linework": ["clean contours"]},
                source=source,
                confidence=0.75,
                evidence=("caller supplied",),
                generated_by="test-provider",
            )
            self.assertEqual(profile.source, source)
            self.assertEqual(profile.features[0].source, source)
            self.assertEqual(profile.confidence, 0.75)
            self.assertEqual(profile.generated_by, "test-provider")

    def test_style_profile_conversion_is_database_independent(self):
        source_profile = {
            "linework": ["clean contours", "tapered strokes"],
            "lighting": "soft illumination",
            "custom_category": "user supplied trait",
        }
        result = engine.build_semantic_style_profile(source_profile, source="user")
        self.assertIsInstance(result, engine.SemanticStyleProfile)
        self.assertEqual(len(result.features), 4)
        self.assertIn("custom_category", {item.category for item in result.features})

    def test_rank_features_orders_by_importance(self):
        features = (
            engine.Feature("mood", "calm", priority=0.4),
            engine.Feature("linework", "clean", priority=0.9),
            engine.Feature("lighting", "soft", priority=0.7),
        )
        ranked = engine.rank_features(features)
        self.assertEqual([item.value for item in ranked], ["clean", "soft", "calm"])

    def test_deduplicate_features_keeps_stronger_duplicate(self):
        features = (
            engine.Feature("linework", "Clean contours", priority=0.5),
            engine.Feature("rendering", " clean   contours ", priority=0.9),
            engine.Feature("lighting", "soft light", priority=0.7),
        )
        unique = engine.deduplicate_features(features)
        self.assertEqual(len(unique), 2)
        strongest = next(item for item in unique if item.value.strip() != "soft light")
        self.assertEqual(strongest.priority, 0.9)
        self.assertEqual(strongest.category, "rendering")

    def test_prompt_units_preserve_feature_metadata(self):
        semantic = engine.semanticize_style_profile(
            {
                "linework": ["clean contours"],
                "lighting": ["soft illumination"],
            },
            source="builtin",
            confidence=0.8,
            evidence={"linework": ["database linework field"]},
            generated_by="style_engine",
        )
        units = engine.to_prompt_units(semantic)
        self.assertEqual(len(units), 2)
        self.assertTrue(all(isinstance(unit, engine.PromptUnit) for unit in units))
        self.assertEqual(units[0].category, "linework")
        self.assertEqual(units[0].text, "clean contours")
        self.assertEqual(units[0].source, "builtin")
        self.assertEqual(units[0].confidence, 0.8)
        self.assertEqual(units[0].evidence, ("database linework field",))


if __name__ == "__main__":
    unittest.main()
