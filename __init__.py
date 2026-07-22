"""ComfyUI-ArtistStyleTranslator node registration."""

from .nodes import (
    ArtistStylePromptMerge,
    ArtistStyleSelector,
    ArtistStyleTranslator,
)

NODE_CLASS_MAPPINGS = {
    "ArtistStyleSelector": ArtistStyleSelector,
    "ArtistStyleTranslator": ArtistStyleTranslator,
    "ArtistStylePromptMerge": ArtistStylePromptMerge,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtistStyleSelector": "Artist Style Selector",
    "ArtistStyleTranslator": "Artist Style Translator",
    "ArtistStylePromptMerge": "Artist Style Prompt Merge",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
