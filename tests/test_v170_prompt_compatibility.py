"""Golden regression for every pre-V1.7 built-in prompt combination."""

import hashlib
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import unittest


def load_project_modules():
    root = Path(__file__).resolve().parents[1]
    package_name = "artist_style_translator_v170_prompt_compatibility_tests"
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
        import_module(f"{package_name}.artist_database"),
        import_module(f"{package_name}.prompt_builder"),
    )


database, prompt_builder = load_project_modules()


class V170PromptCompatibilityTests(unittest.TestCase):
    def test_all_31_artists_models_and_detail_levels_match_v165_baseline(self):
        rows = [
            (
                artist,
                model,
                detail,
                prompt_builder.build_prompt(artist, model, detail),
            )
            for artist in database.list_artists()
            for model in prompt_builder.TARGET_MODELS
            for detail in prompt_builder.DETAIL_LEVELS
        ]
        serialized = json.dumps(
            rows,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        self.assertEqual(len(rows), 31 * 5 * 3)
        self.assertEqual(
            hashlib.sha256(serialized).hexdigest(),
            "3370151de1573cfaab183dc190063d0c5e80193bfdc3ee4798d7a09f06bf03f7",
        )


if __name__ == "__main__":
    unittest.main()
