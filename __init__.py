"""ComfyUI-ArtistStyleTranslator node registration."""

from .nodes import ArtistStylePromptMerge, ArtistStyleTranslator

NODE_CLASS_MAPPINGS = {
    "ArtistStyleTranslator": ArtistStyleTranslator,
    "ArtistStylePromptMerge": ArtistStylePromptMerge,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtistStyleTranslator": "Artist Style Translator",
    "ArtistStylePromptMerge": "Artist Style Prompt Merge",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
