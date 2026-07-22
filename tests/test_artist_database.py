"""Tests for the structured built-in artist database."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest


def load_database_module():
    path = Path(__file__).resolve().parents[1] / "artist_database.py"
    spec = spec_from_file_location("artist_style_translator_database_tests", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load artist database")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


database = load_database_module()


def load_style_engine():
    path = Path(__file__).resolve().parents[1] / "style_engine.py"
    name = "artist_style_translator_database_semantic_tests"
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load style engine")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


style_engine = load_style_engine()
REFINED_ARTISTS = ("WLOP", "Guweiz", "Sakimichan", "Artgerm")
V14_EXPANSION_ARTISTS = (
    "Ilya Kuvshinov",
    "Mai Yoneyama",
    "redjuice",
    "lack",
    "Hiten",
    "Greg Rutkowski",
    "Craig Mullins",
    "Feng Zhu",
    "Jama Jurabaev",
    "LAM",
    "Krenz Cushart",
    "Even Amundsen",
    "Ruan Jia",
)
V14_NEW_ARTISTS = (
    "Ilya Kuvshinov",
    "Mai Yoneyama",
    "Greg Rutkowski",
    "Craig Mullins",
    "Feng Zhu",
    "Jama Jurabaev",
    "Even Amundsen",
    "Ruan Jia",
)


class ArtistDatabaseTests(unittest.TestCase):
    def test_known_artist_matches(self):
        artist = database.get_artist("Yaegashi Nan")
        self.assertIsInstance(artist, dict)
        self.assertEqual(artist["canonical_name"], "Yaegashi Nan")

    def test_lookup_is_case_insensitive(self):
        self.assertEqual(database.get_artist("wlop")["canonical_name"], "WLOP")

    def test_alias_and_separator_variations_match(self):
        self.assertEqual(database.get_artist("Tony")["canonical_name"], "Tony Taka")
        self.assertEqual(
            database.get_artist("coffee kizoku")["canonical_name"],
            "Coffee-kizoku",
        )

    def test_unknown_artist_returns_none(self):
        self.assertIsNone(database.get_artist("Unknown Demo Artist"))

    def test_all_artists_are_preserved_and_sorted_after_v14_expansion(self):
        artists = database.list_artists()
        self.assertIsInstance(artists, list)
        self.assertEqual(len(artists), 32)
        self.assertIn("Homare", artists)
        self.assertEqual(artists, sorted(artists, key=str.casefold))

    def test_profiles_have_complete_uniform_schema(self):
        expected = set(database.STYLE_PROFILE_FIELDS)
        schemas = set()
        for name in database.list_artists():
            entry = database.get_artist(name)
            self.assertEqual(set(entry), {"canonical_name", "aliases", "style_profile"})
            self.assertEqual(set(entry["style_profile"]), expected)
            schemas.add(tuple(entry["style_profile"]))
            for value in entry["style_profile"].values():
                self.assertIsInstance(value, tuple)
        self.assertEqual(len(schemas), 1)

    def test_database_contains_no_prebuilt_prompt_field(self):
        prohibited = {"prompt", "final_prompt", "visual_traits"}
        for name in database.list_artists():
            entry = database.get_artist(name)
            self.assertTrue(prohibited.isdisjoint(entry))
            self.assertTrue(prohibited.isdisjoint(entry["style_profile"]))

    def test_four_refined_artists_have_valid_style_profiles(self):
        expected = set(database.STYLE_PROFILE_FIELDS)
        for name in REFINED_ARTISTS:
            entry = database.get_artist(name)
            self.assertIsNotNone(entry)
            self.assertEqual(entry["canonical_name"], name)
            self.assertEqual(set(entry["style_profile"]), expected)
            self.assertTrue(all(entry["style_profile"].values()))

    def test_four_refined_artists_generate_distinct_feature_sets(self):
        feature_sets = {}
        for name in REFINED_ARTISTS:
            profile = database.get_artist(name)["style_profile"]
            semantic = style_engine.semanticize_style_profile(
                profile,
                source="builtin",
                confidence=0.95,
                generated_by="artist_database",
            )
            feature_sets[name] = {
                (feature.category, feature.value.casefold())
                for feature in semantic.features
            }
            self.assertGreaterEqual(len(feature_sets[name]), 25)

        for index, first_name in enumerate(REFINED_ARTISTS):
            for second_name in REFINED_ARTISTS[index + 1:]:
                first = feature_sets[first_name]
                second = feature_sets[second_name]
                self.assertGreaterEqual(len(first - second), 20)
                self.assertGreaterEqual(len(second - first), 20)

    def test_refined_profiles_keep_distinct_semantic_focus(self):
        expected_phrases = {
            "WLOP": "large-scale world building",
            "Guweiz": "detailed armor and clothing design",
            "Sakimichan": "smooth skin finish",
            "Artgerm": "commercial digital illustration",
        }
        for name, phrase in expected_phrases.items():
            profile = database.get_artist(name)["style_profile"]
            flattened = {
                value.casefold()
                for values in profile.values()
                for value in values
            }
            self.assertIn(phrase.casefold(), flattened)

    def test_v14_artists_have_valid_complete_profiles(self):
        expected = set(database.STYLE_PROFILE_FIELDS)
        for name in V14_EXPANSION_ARTISTS:
            entry = database.get_artist(name)
            self.assertIsNotNone(entry)
            self.assertEqual(entry["canonical_name"], name)
            self.assertEqual(set(entry["style_profile"]), expected)
            self.assertTrue(all(entry["style_profile"].values()))

    def test_each_new_v14_artist_has_nonempty_semantic_features(self):
        for name in V14_NEW_ARTISTS:
            profile = database.get_artist(name)["style_profile"]
            semantic = style_engine.semanticize_style_profile(
                profile,
                source="builtin",
                confidence=0.95,
                generated_by="artist_database",
            )
            self.assertGreaterEqual(len(semantic.features), 25)
            self.assertTrue(all(feature.value.strip() for feature in semantic.features))

    def test_major_v14_artist_pairs_have_distinct_feature_sets(self):
        feature_sets = {}
        for name in V14_EXPANSION_ARTISTS:
            profile = database.get_artist(name)["style_profile"]
            semantic = style_engine.semanticize_style_profile(profile)
            feature_sets[name] = {
                (feature.category, feature.value.casefold())
                for feature in semantic.features
            }

        for index, first_name in enumerate(V14_EXPANSION_ARTISTS):
            for second_name in V14_EXPANSION_ARTISTS[index + 1:]:
                first = feature_sets[first_name]
                second = feature_sets[second_name]
                self.assertNotEqual(first, second)
                overlap = len(first & second)
                union = len(first | second)
                self.assertLess(overlap / union, 0.5)

    def test_profiles_do_not_embed_artist_names_or_attribution_phrases(self):
        prohibited = ("in the style of", "inspired by")
        for name in V14_EXPANSION_ARTISTS:
            profile = database.get_artist(name)["style_profile"]
            text = " ".join(value for values in profile.values() for value in values)
            lowered = text.casefold()
            self.assertTrue(all(phrase not in lowered for phrase in prohibited))
            canonical_words = tuple(name.casefold().replace("-", " ").split())
            text_words = {
                word.strip(".,;:-_()")
                for word in lowered.split()
            }
            if len(canonical_words) == 1:
                self.assertNotIn(canonical_words[0], text_words)
            else:
                self.assertNotIn(" ".join(canonical_words), lowered)


if __name__ == "__main__":
    unittest.main()
