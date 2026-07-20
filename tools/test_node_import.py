"""Standalone import and registration smoke test."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def load_project_package():
    project_root = Path(__file__).resolve().parents[1]
    package_name = "comfyui_artist_style_translator_import_test"
    spec = spec_from_file_location(
        package_name,
        project_root / "__init__.py",
        submodule_search_locations=[str(project_root)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to create an import specification")
    module = module_from_spec(spec)
    sys.modules[package_name] = module
    spec.loader.exec_module(module)
    return module


def main():
    package = load_project_package()
    assert hasattr(package, "NODE_CLASS_MAPPINGS")
    assert hasattr(package, "NODE_DISPLAY_NAME_MAPPINGS")
    assert "ArtistStyleTranslator" in package.NODE_CLASS_MAPPINGS
    assert "ArtistStylePromptMerge" in package.NODE_CLASS_MAPPINGS
    assert package.NODE_DISPLAY_NAME_MAPPINGS.get(
        "ArtistStyleTranslator"
    ) == "Artist Style Translator"
    assert package.NODE_DISPLAY_NAME_MAPPINGS.get(
        "ArtistStylePromptMerge"
    ) == "Artist Style Prompt Merge"

    node_class = package.NODE_CLASS_MAPPINGS["ArtistStyleTranslator"]
    node = node_class()
    required = node_class.INPUT_TYPES()["required"]
    assert required["artist_name"][0] == "STRING"
    assert required["artist_name"][1]["multiline"] is True
    assert required["artist_name"][1]["default"] == "Yaegashi Nan"
    assert tuple(required["target_model"][0]) == (
        "Generic", "Z-Image", "FLUX", "Qwen-Image", "Krea"
    )
    assert required["target_model"][1]["default"] == "Z-Image"
    assert tuple(required["detail_level"][0]) == (
        "Short", "Standard", "Detailed"
    )
    assert required["detail_level"][1]["default"] == "Standard"

    result = node.translate_style("  Yaegashi Nan  ", "Z-Image", "Standard")
    assert isinstance(result, tuple) and len(result) == 1
    assert isinstance(result[0], str) and result[0]
    assert "Yaegashi Nan" not in result[0]
    assert "in the style of" not in result[0].casefold()

    merge_class = package.NODE_CLASS_MAPPINGS["ArtistStylePromptMerge"]
    merge_node = merge_class()
    merge_required = merge_class.INPUT_TYPES()["required"]
    assert merge_required["base_prompt"][0] == "STRING"
    assert merge_required["style_prompt"][0] == "STRING"
    assert merge_required["style_prompt"][1]["forceInput"] is True
    merged = merge_node.merge_prompts("base prompt", result[0])
    assert isinstance(merged, tuple) and len(merged) == 1
    assert merged[0].startswith("base prompt\n\n")
    assert result[0] in merged[0]
    print("Import and registration checks passed.")


if __name__ == "__main__":
    main()
