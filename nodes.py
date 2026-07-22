"""ComfyUI node definition for Artist Style Translator."""

from .prompt_builder import DETAIL_LEVELS, TARGET_MODELS, build_prompt
from .providers.builtin_provider import BuiltinSemanticProvider


class ArtistStyleSelector:
    """Select one canonical artist name exposed by the provider contract."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "artist": (
                    BuiltinSemanticProvider().list_artists(),
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("artist_name",)
    FUNCTION = "select_artist"
    CATEGORY = "prompt/artist_style"

    def select_artist(self, artist):
        return (artist,)


class ArtistStyleTranslator:
    """Build an offline visual style prompt from an artist name."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "artist_name": (
                    "STRING",
                    {
                        "default": "Yaegashi Nan",
                        "multiline": True,
                    },
                ),
                "target_model": (
                    TARGET_MODELS,
                    {"default": "Z-Image"},
                ),
                "detail_level": (
                    DETAIL_LEVELS,
                    {"default": "Standard"},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "translate_style"
    CATEGORY = "prompt/artist_style"

    def translate_style(
        self,
        artist_name,
        target_model="Z-Image",
        detail_level="Standard",
    ):
        return (build_prompt(artist_name, target_model, detail_level),)


class ArtistStylePromptMerge:
    """Cleanly append a generated style prompt to an editable base prompt."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                    },
                ),
                "style_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "forceInput": True,
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("final_prompt",)
    FUNCTION = "merge_prompts"
    CATEGORY = "prompt/artist_style"

    def merge_prompts(self, base_prompt, style_prompt):
        try:
            base = str(base_prompt or "").strip()
        except Exception:
            base = ""
        try:
            style = str(style_prompt or "").strip()
        except Exception:
            style = ""

        return ("\n\n".join(part for part in (base, style) if part),)
