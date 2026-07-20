"""Tests for structured offline prompt construction."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_prompt_builder():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_prompt_tests"
    package_spec = spec_from_file_location(
        package_name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    if package_spec is None or package_spec.loader is None:
        raise RuntimeError("Unable to load project package")
    package = module_from_spec(package_spec)
    sys.modules[package_name] = package
    package_spec.loader.exec_module(package)
    return sys.modules[f"{package_name}.prompt_builder"]


prompt_builder = load_prompt_builder()


class PromptBuilderTests(unittest.TestCase):
    def test_real_production_context_uses_semantic_engine_objects(self):
        context = prompt_builder.build_semantic_profile_for_artist(
            "WLOP", "Standard"
        )
        self.assertIsInstance(
            context.semantic_profile,
            prompt_builder.SemanticStyleProfile,
        )
        self.assertTrue(
            all(
                isinstance(feature, prompt_builder.Feature)
                for feature in context.ranked_features
            )
        )
        self.assertTrue(
            all(
                isinstance(unit, prompt_builder.PromptUnit)
                for unit in context.prompt_units
            )
        )

    def test_builtin_provenance_survives_to_prompt_units(self):
        context = prompt_builder.build_semantic_profile_for_artist(
            "Yaegashi Nan", "Detailed"
        )
        self.assertEqual(context.semantic_profile.source, "builtin")
        self.assertTrue(context.semantic_profile.features)
        for feature in context.semantic_profile.features:
            self.assertEqual(feature.source, "builtin")
            self.assertEqual(feature.confidence, 0.95)
            self.assertEqual(feature.generated_by, "artist_database")
        for unit in context.prompt_units:
            self.assertEqual(unit.source, "builtin")
            self.assertEqual(unit.confidence, 0.95)
            self.assertTrue(unit.evidence)

    def test_detail_levels_select_distinct_semantic_unit_counts(self):
        counts = [
            len(
                prompt_builder.build_semantic_profile_for_artist(
                    "WLOP", detail
                ).prompt_units
            )
            for detail in prompt_builder.DETAIL_LEVELS
        ]
        self.assertEqual(counts, [8, 14, 21])

    def test_short_selection_prioritizes_core_categories(self):
        context = prompt_builder.build_semantic_profile_for_artist("WLOP", "Short")
        categories = [unit.category for unit in context.prompt_units]
        self.assertEqual(categories[:3], ["medium", "medium", "genre"])
        self.assertIn("linework", categories)
        self.assertNotIn("mood", categories)

    def test_semantic_deduplication_precedes_prompt_units(self):
        context = prompt_builder.build_semantic_profile_for_artist(
            "WLOP", "Detailed"
        )
        values = [" ".join(unit.text.casefold().split()) for unit in context.prompt_units]
        self.assertEqual(len(values), len(set(values)))
        self.assertLessEqual(
            len(context.deduplicated_features),
            len(context.ranked_features),
        )

    def test_unknown_and_empty_inputs_also_use_semantic_engine(self):
        unknown = prompt_builder.build_semantic_profile_for_artist(
            "Unknown Demo Artist", "Standard"
        )
        empty = prompt_builder.build_semantic_profile_for_artist("", "Standard")
        for context in (unknown, empty):
            self.assertIsInstance(
                context.semantic_profile,
                prompt_builder.SemanticStyleProfile,
            )
            self.assertEqual(context.semantic_profile.source, "builtin")
            self.assertEqual(context.semantic_profile.confidence, 0.85)
            self.assertEqual(
                context.semantic_profile.generated_by,
                "prompt_builder.fallback",
            )
            self.assertTrue(context.prompt_units)

    def test_final_prompt_matches_real_semantic_adapter_path(self):
        context = prompt_builder.build_semantic_profile_for_artist(
            "WLOP", "Standard"
        )
        expected = prompt_builder.adapt_style_profile(
            context.prompt_units,
            "Z-Image",
            "Standard",
        )
        self.assertEqual(
            prompt_builder.build_prompt("WLOP", "Z-Image", "Standard"),
            expected,
        )

    def test_unknown_empty_and_chinese_inputs_use_safe_fallback(self):
        values = [
            prompt_builder.build_prompt("Unknown Demo Artist"),
            prompt_builder.build_prompt(""),
            prompt_builder.build_prompt("齐白石"),
        ]
        for value in values:
            self.assertIsInstance(value, str)
            self.assertTrue(value)
        self.assertEqual(values[0], values[1])
        self.assertEqual(values[1], values[2])

    def test_three_artist_outputs_are_clearly_different(self):
        values = {
            name: prompt_builder.build_prompt(name, "Z-Image", "Standard")
            for name in ("Yaegashi Nan", "WLOP", "Mika Pikazo")
        }
        self.assertEqual(len(set(values.values())), 3)
        starts = {tuple(value.split(", ")[:4]) for value in values.values()}
        self.assertEqual(len(starts), 3)

    def test_all_target_models_return_distinct_nonempty_text(self):
        outputs = []
        for model in prompt_builder.TARGET_MODELS:
            result = prompt_builder.build_prompt("WLOP", model, "Standard")
            self.assertIsInstance(result, str)
            self.assertTrue(result)
            outputs.append(result)
        self.assertGreaterEqual(len(set(outputs)), 3)

    def test_detail_levels_increase_output_length(self):
        lengths = [
            len(prompt_builder.build_prompt("WLOP", "Z-Image", detail))
            for detail in prompt_builder.DETAIL_LEVELS
        ]
        self.assertLess(lengths[0], lengths[1])
        self.assertLess(lengths[1], lengths[2])

    def test_repeated_calls_are_stable(self):
        first = prompt_builder.build_prompt("Mika Pikazo", "Qwen-Image", "Detailed")
        second = prompt_builder.build_prompt("Mika Pikazo", "Qwen-Image", "Detailed")
        self.assertEqual(first, second)

    def test_output_omits_names_and_prohibited_attribution(self):
        cases = (("Tony", "Tony"), ("WLOP", "WLOP"), ("Mika Pikazo", "Mika Pikazo"))
        for query, name in cases:
            lowered = prompt_builder.build_prompt(query, "FLUX", "Detailed").casefold()
            self.assertNotIn(name.casefold(), lowered)
            self.assertNotIn("in the style of", lowered)
            self.assertNotIn("inspired by", lowered)

    def test_comma_phrase_outputs_have_no_exact_duplicates(self):
        for model in ("Generic", "Z-Image", "Krea"):
            result = prompt_builder.build_prompt("WLOP", model, "Detailed")
            phrases = [part.strip().casefold() for part in result.split(",")]
            self.assertEqual(len(phrases), len(set(phrases)))

    def test_invalid_controls_fall_back_safely(self):
        result = prompt_builder.build_prompt(None, "Invalid", "Invalid")
        self.assertIsInstance(result, str)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
