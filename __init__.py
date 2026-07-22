"""ComfyUI-ArtistStyleTranslator node registration."""

from .nodes import (
    ArtistStylePromptMerge,
    ArtistStyleSelector,
    ArtistStyleTranslator,
    ArtistStyleTranslatorAdvanced,
    SemanticProfilePreview,
)

NODE_CLASS_MAPPINGS = {
    "ArtistStyleSelector": ArtistStyleSelector,
    "ArtistStyleTranslator": ArtistStyleTranslator,
    "ArtistStyleTranslatorAdvanced": ArtistStyleTranslatorAdvanced,
    "SemanticProfilePreview": SemanticProfilePreview,
    "ArtistStylePromptMerge": ArtistStylePromptMerge,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtistStyleSelector": "Artist Style Selector",
    "ArtistStyleTranslator": "Artist Style Translator",
    "ArtistStyleTranslatorAdvanced": "Artist Style Translator Advanced",
    "SemanticProfilePreview": "Semantic Profile Preview",
    "ArtistStylePromptMerge": "Artist Style Prompt Merge",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
