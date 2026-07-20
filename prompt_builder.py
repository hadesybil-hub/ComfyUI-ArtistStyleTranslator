"""Offline orchestration through the semantic style engine."""

from dataclasses import dataclass

from .artist_database import (
    STYLE_PROFILE_FIELDS,
    get_artist,
    normalize_artist_name,
)
from .model_adapters import (
    SUPPORTED_DETAIL_LEVELS,
    SUPPORTED_MODELS,
    adapt_style_profile,
    normalize_detail_level,
)
from .style_engine import (
    Feature,
    PromptUnit,
    SemanticStyleProfile,
    deduplicate_features,
    rank_features,
    semanticize_style_profile,
    to_prompt_units,
)


TARGET_MODELS = SUPPORTED_MODELS
DETAIL_LEVELS = SUPPORTED_DETAIL_LEVELS

_DETAIL_UNIT_COUNTS = {"Short": 8, "Standard": 14, "Detailed": 21}

GENERIC_STYLE_PROFILE = {
    "medium": ("digital character illustration",),
    "genre": ("contemporary visual storytelling",),
    "subject_focus": ("character-focused imagery",),
    "linework": ("clean controlled linework",),
    "shape_language": ("clear readable silhouettes",),
    "facial_design": ("detailed facial features",),
    "anatomy": ("coherent natural proportions",),
    "rendering": ("polished surface rendering",),
    "shading": ("controlled form shading",),
    "coloring": ("coherent color relationships",),
    "palette": ("balanced color palette",),
    "lighting": ("clear directional illumination",),
    "composition": ("balanced focal composition",),
    "environment": ("subtle spatial context",),
    "clothing": ("carefully rendered clothing",),
    "mood": ("composed visual mood",),
    "detail_emphasis": ("faces; clothing; material definition",),
}


@dataclass(frozen=True, slots=True)
class SemanticPromptContext:
    """Inspectable semantic state immediately before model adaptation."""

    semantic_profile: SemanticStyleProfile
    ranked_features: tuple[Feature, ...]
    deduplicated_features: tuple[Feature, ...]
    prompt_units: tuple[PromptUnit, ...]
    detail_level: str


def _valid_profile(profile):
    return isinstance(profile, dict) and all(
        field in profile for field in STYLE_PROFILE_FIELDS
    )


def build_semantic_profile_for_artist(artist_name, detail_level="Standard"):
    """Build the real, selected semantic context used by production prompts."""
    normalized_name = normalize_artist_name(artist_name)
    artist = get_artist(normalized_name)
    profile = artist.get("style_profile") if artist else GENERIC_STYLE_PROFILE
    known_artist = artist is not None and _valid_profile(profile)
    if not known_artist:
        profile = GENERIC_STYLE_PROFILE

    semantic_profile = semanticize_style_profile(
        profile,
        source="builtin",
        confidence=0.95 if known_artist else 0.85,
        evidence=(
            "builtin structured style profile"
            if known_artist
            else "builtin generic fallback profile",
        ),
        generated_by=(
            "artist_database" if known_artist else "prompt_builder.fallback"
        ),
    )
    ranked = rank_features(semantic_profile)
    deduplicated = deduplicate_features(ranked)
    all_units = to_prompt_units(deduplicated)
    detail = normalize_detail_level(detail_level)
    selected = all_units[: _DETAIL_UNIT_COUNTS[detail]]
    return SemanticPromptContext(
        semantic_profile=semantic_profile,
        ranked_features=ranked,
        deduplicated_features=deduplicated,
        prompt_units=selected,
        detail_level=detail,
    )


def build_prompt(artist_name, target_model="Z-Image", detail_level="Standard"):
    """Build deterministic plain text through the semantic production chain."""
    try:
        context = build_semantic_profile_for_artist(artist_name, detail_level)
        result = adapt_style_profile(
            context.prompt_units,
            target_model,
            context.detail_level,
        )
        if isinstance(result, str) and result.strip():
            return result.strip()
    except Exception:
        pass

    fallback = build_semantic_profile_for_artist("", "Standard")
    return adapt_style_profile(fallback.prompt_units, "Z-Image", "Standard")
