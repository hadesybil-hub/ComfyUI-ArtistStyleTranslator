"""Unit tests for the ComfyUI node interface."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_project_package():
    root = Path(__file__).resolve().parents[1]
    name = "artist_style_translator_node_tests"
    spec = spec_from_file_location(
        name,
        root / "__init__.py",
        submodule_search_locations=[str(root)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load project package")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ArtistStyleTranslator = load_project_package().NODE_CLASS_MAPPINGS[
    "ArtistStyleTranslator"
]
ArtistStylePromptMerge = load_project_package().NODE_CLASS_MAPPINGS[
    "ArtistStylePromptMerge"
]


class ArtistStyleTranslatorTests(unittest.TestCase):
    def setUp(self):
        self.node = ArtistStyleTranslator()

    def test_english_artist_name(self):
        result = self.node.translate_style("Yaegashi Nan")
        self.assertTrue(result[0])
        self.assertNotIn("Yaegashi Nan", result[0])

    def test_surrounding_whitespace_is_removed_for_lookup(self):
        clean = self.node.translate_style("Yaegashi Nan")
        padded = self.node.translate_style("  Yaegashi Nan  ")
        self.assertEqual(clean, padded)

    def test_empty_string_does_not_raise(self):
        self.assertTrue(self.node.translate_style("")[0])

    def test_chinese_input_does_not_raise(self):
        self.assertTrue(self.node.translate_style("齐白石")[0])

    def test_multiline_input_does_not_raise(self):
        self.assertTrue(self.node.translate_style("Artist One\nArtist Two")[0])

    def test_result_is_single_element_tuple(self):
        result = self.node.translate_style("Test Artist")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], str)

    def test_input_types_include_required_controls(self):
        required = ArtistStyleTranslator.INPUT_TYPES()["required"]
        self.assertEqual(required["artist_name"][0], "STRING")
        self.assertTrue(required["artist_name"][1]["multiline"])
        self.assertEqual(required["target_model"][1]["default"], "Z-Image")
        self.assertEqual(required["detail_level"][1]["default"], "Standard")


class ArtistStylePromptMergeTests(unittest.TestCase):
    def setUp(self):
        self.node = ArtistStylePromptMerge()

    def test_base_and_style_are_cleanly_combined(self):
        result = self.node.merge_prompts("  a portrait  ", "  soft linework  ")
        self.assertEqual(result, ("a portrait\n\nsoft linework",))

    def test_empty_inputs_are_safe(self):
        self.assertEqual(self.node.merge_prompts("base", ""), ("base",))
        self.assertEqual(self.node.merge_prompts("", "style"), ("style",))
        self.assertEqual(self.node.merge_prompts("", ""), ("",))

    def test_merge_returns_single_element_tuple(self):
        result = self.node.merge_prompts("base", "style")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], str)

    def test_merge_node_input_interface(self):
        required = ArtistStylePromptMerge.INPUT_TYPES()["required"]
        self.assertEqual(required["base_prompt"][0], "STRING")
        self.assertTrue(required["base_prompt"][1]["multiline"])
        self.assertEqual(required["style_prompt"][0], "STRING")
        self.assertTrue(required["style_prompt"][1]["forceInput"])


if __name__ == "__main__":
    unittest.main()
