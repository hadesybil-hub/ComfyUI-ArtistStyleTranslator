"""Deterministic model-specific rendering of semantic PromptUnit objects."""

from collections.abc import Mapping

from .style_engine import (
    Feature,
    PromptUnit,
    SemanticStyleProfile,
    semanticize_style_profile,
    to_prompt_units,
)


SUPPORTED_MODELS = ("Generic", "Z-Image", "FLUX", "Qwen-Image", "Krea")
SUPPORTED_DETAIL_LEVELS = ("Short", "Standard", "Detailed")

_BASE_COUNTS = {"Short": 8, "Standard": 14, "Detailed": 21}
_KREA_COUNTS = {"Short": 5, "Standard": 8, "Detailed": 11}


def normalize_target_model(target_model):
    """Return a supported display name, defaulting to Z-Image."""
    try:
        key = str(target_model or "").strip().casefold()
    except Exception:
        return "Z-Image"
    return {model.casefold(): model for model in SUPPORTED_MODELS}.get(key, "Z-Image")


def normalize_detail_level(detail_level):
    """Return a supported detail level, defaulting to Standard."""
    try:
        key = str(detail_level or "").strip().casefold()
    except Exception:
        return "Standard"
    return {
        level.casefold(): level for level in SUPPORTED_DETAIL_LEVELS
    }.get(key, "Standard")


def _coerce_prompt_units(style_input, detail):
    """Compatibility bridge; every path is normalized by style_engine."""
    requires_selection = False
    if isinstance(style_input, Mapping):
        semantic = semanticize_style_profile(
            style_input,
            source="builtin",
            confidence=0.9,
            generated_by="model_adapters.compatibility",
        )
        units = to_prompt_units(semantic)
        requires_selection = True
    elif isinstance(style_input, SemanticStyleProfile):
        units = to_prompt_units(style_input)
        requires_selection = True
    else:
        values = tuple(style_input or ())
        if all(isinstance(item, PromptUnit) for item in values):
            units = values
        elif all(isinstance(item, Feature) for item in values):
            units = to_prompt_units(values)
            requires_selection = True
        else:
            raise TypeError("Adapter input must contain semantic features or prompt units")

    if requires_selection:
        units = units[: _BASE_COUNTS[detail]]
    return tuple(units)


def _natural_join(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + ", and " + items[-1]


def _sentence(text):
    clean = text.strip().rstrip(". ")
    return clean[:1].upper() + clean[1:] + "." if clean else ""


def _adapt_flux(features, detail):
    if detail == "Short":
        return _sentence(
            f"The image combines {_natural_join(features[:4])}, shaped by "
            f"{_natural_join(features[4:])}"
        )
    sentences = [
        _sentence(f"The image combines {_natural_join(features[:5])}"),
        _sentence(
            f"Its material, light, space, and composition are defined by "
            f"{_natural_join(features[5:14])}"
        ),
    ]
    if detail == "Detailed" and len(features) > 14:
        sentences.append(
            _sentence(
                f"Secondary visual detail includes {_natural_join(features[14:])}, "
                "kept subordinate to the main focal structure"
            )
        )
    return " ".join(sentences)


def _adapt_qwen(features, detail):
    first = _sentence(
        f"The visual direction uses {_natural_join(features[:6])}"
    )
    if detail == "Short":
        return first
    second = _sentence(
        f"Color, light, rendering, and composition remain clear through "
        f"{_natural_join(features[6:13])}"
    )
    if detail == "Standard" or len(features) <= 13:
        return f"{first} {second}"
    third = _sentence(
        f"Additional context comes from {_natural_join(features[13:])}"
    )
    return f"{first} {second} {third}"


def adapt_style_profile(style_input, target_model="Z-Image", detail_level="Standard"):
    """Render selected semantic units while preserving the legacy entry point."""
    model = normalize_target_model(target_model)
    detail = normalize_detail_level(detail_level)
    try:
        units = _coerce_prompt_units(style_input, detail)
        if model == "Krea":
            units = units[: _KREA_COUNTS[detail]]
        features = [unit.text for unit in units]
        minimum = 5 if model == "Krea" else 6
        if len(features) < minimum:
            raise ValueError("Not enough semantic prompt units")

        if model == "Generic":
            return ", ".join(features)
        if model == "Z-Image":
            return f"{features[0]}, with {_natural_join(features[1:])}"
        if model == "FLUX":
            return _adapt_flux(features, detail)
        if model == "Qwen-Image":
            return _adapt_qwen(features, detail)
        return ", ".join(features)
    except Exception:
        return (
            "digital character illustration, clean linework, controlled shading, "
            "coherent colors, balanced composition, clear lighting, polished rendering"
        )
