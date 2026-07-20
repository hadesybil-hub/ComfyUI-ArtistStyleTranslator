"""Provider-agnostic conversion from style profiles to semantic features.

This module does not generate prompts and has no ComfyUI, model, database,
network, or Ollama dependencies.
"""

from dataclasses import dataclass, field
from typing import Iterable, Mapping


SUPPORTED_SOURCES = ("builtin", "ollama", "web", "user")

_CATEGORY_PRIORITIES = {
    "medium": 1.00,
    "genre": 0.98,
    "linework": 0.96,
    "shape_language": 0.94,
    "facial_design": 0.92,
    "rendering": 0.90,
    "coloring": 0.88,
    "palette": 0.86,
    "lighting": 0.84,
    "composition": 0.82,
    "subject_focus": 0.78,
    "anatomy": 0.76,
    "shading": 0.74,
    "environment": 0.72,
    "clothing": 0.70,
    "mood": 0.68,
    "detail_emphasis": 0.66,
}


def _normalized_text(value, fallback=""):
    try:
        text = str(value if value is not None else "").strip()
    except Exception:
        return fallback
    return text or fallback


def _normalized_score(value, fallback):
    try:
        score = float(value)
    except (TypeError, ValueError, OverflowError):
        score = fallback
    return max(0.0, min(1.0, score))


def _evidence_tuple(value):
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    try:
        return tuple(
            text
            for item in value
            if (text := _normalized_text(item))
        )
    except TypeError:
        text = _normalized_text(value)
        return (text,) if text else ()


@dataclass(frozen=True, slots=True)
class Feature:
    """One normalized semantic style feature with provenance metadata."""

    category: str
    value: str
    priority: float = 0.5
    source: str = "builtin"
    confidence: float = 1.0
    evidence: tuple[str, ...] = field(default_factory=tuple)
    generated_by: str = "style_engine"

    def __post_init__(self):
        category = _normalized_text(self.category)
        value = _normalized_text(self.value)
        if not category or not value:
            raise ValueError("Feature category and value must be non-empty")
        object.__setattr__(self, "category", category)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "priority", _normalized_score(self.priority, 0.5))
        object.__setattr__(self, "source", _normalized_text(self.source, "builtin"))
        object.__setattr__(self, "confidence", _normalized_score(self.confidence, 1.0))
        object.__setattr__(self, "evidence", _evidence_tuple(self.evidence))
        object.__setattr__(
            self,
            "generated_by",
            _normalized_text(self.generated_by, "style_engine"),
        )


@dataclass(frozen=True, slots=True)
class SemanticStyleProfile:
    """A provider-neutral collection of semantic style features."""

    features: tuple[Feature, ...]
    source: str = "builtin"
    confidence: float = 1.0
    evidence: tuple[str, ...] = field(default_factory=tuple)
    generated_by: str = "style_engine"

    def __post_init__(self):
        features = tuple(self.features)
        if not all(isinstance(item, Feature) for item in features):
            raise TypeError("SemanticStyleProfile features must be Feature objects")
        object.__setattr__(self, "features", features)
        object.__setattr__(self, "source", _normalized_text(self.source, "builtin"))
        object.__setattr__(self, "confidence", _normalized_score(self.confidence, 1.0))
        object.__setattr__(self, "evidence", _evidence_tuple(self.evidence))
        object.__setattr__(
            self,
            "generated_by",
            _normalized_text(self.generated_by, "style_engine"),
        )


@dataclass(frozen=True, slots=True)
class PromptUnit:
    """A ranked atomic unit for a future prompt layer to consume."""

    category: str
    text: str
    priority: float
    source: str
    confidence: float
    evidence: tuple[str, ...]
    generated_by: str


def _feature_sequence(features):
    if isinstance(features, SemanticStyleProfile):
        return features.features
    return tuple(features or ())


def rank_features(features):
    """Return features ordered by priority and confidence, deterministically."""
    sequence = _feature_sequence(features)
    if not all(isinstance(item, Feature) for item in sequence):
        raise TypeError("rank_features accepts Feature objects")
    return tuple(
        sorted(
            sequence,
            key=lambda item: (
                -item.priority,
                -item.confidence,
                item.category.casefold(),
                item.value.casefold(),
            ),
        )
    )


def deduplicate_features(features):
    """Remove exact semantic duplicates, retaining the strongest instance."""
    sequence = _feature_sequence(features)
    unique = {}
    order = []
    for item in sequence:
        if not isinstance(item, Feature):
            raise TypeError("deduplicate_features accepts Feature objects")
        key = " ".join(item.value.casefold().split())
        current = unique.get(key)
        if current is None:
            unique[key] = item
            order.append(key)
        elif (item.priority, item.confidence) > (
            current.priority,
            current.confidence,
        ):
            unique[key] = item
    return tuple(unique[key] for key in order)


def to_prompt_units(features):
    """Convert deduplicated, ranked features into atomic PromptUnit objects."""
    prepared = rank_features(deduplicate_features(features))
    return tuple(
        PromptUnit(
            category=item.category,
            text=item.value,
            priority=item.priority,
            source=item.source,
            confidence=item.confidence,
            evidence=item.evidence,
            generated_by=item.generated_by,
        )
        for item in prepared
    )


def _profile_values(value):
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(part.strip() for part in value.split(";") if part.strip())
    try:
        return tuple(
            text for item in value if (text := _normalized_text(item))
        )
    except TypeError:
        text = _normalized_text(value)
        return (text,) if text else ()


def semanticize_style_profile(
    style_profile,
    *,
    source="builtin",
    confidence=1.0,
    evidence=(),
    generated_by="style_engine",
):
    """Convert any mapping-shaped style profile into a semantic profile.

    Provenance is supplied by the caller, so future local, web, and user
    providers can use this interface without coupling this module to them.
    """
    if not isinstance(style_profile, Mapping):
        style_profile = {}

    profile_evidence = _evidence_tuple(evidence)
    features = []
    for category, raw_value in style_profile.items():
        clean_category = _normalized_text(category)
        if not clean_category:
            continue
        base_priority = _CATEGORY_PRIORITIES.get(clean_category, 0.5)
        category_evidence = profile_evidence
        if isinstance(evidence, Mapping):
            category_evidence = _evidence_tuple(evidence.get(clean_category))
        for offset, value in enumerate(_profile_values(raw_value)):
            features.append(
                Feature(
                    category=clean_category,
                    value=value,
                    priority=max(0.0, base_priority - (offset * 0.01)),
                    source=source,
                    confidence=confidence,
                    evidence=category_evidence,
                    generated_by=generated_by,
                )
            )

    prepared = rank_features(deduplicate_features(features))
    return SemanticStyleProfile(
        features=prepared,
        source=source,
        confidence=confidence,
        evidence=profile_evidence if not isinstance(evidence, Mapping) else (),
        generated_by=generated_by,
    )


build_semantic_style_profile = semanticize_style_profile


__all__ = [
    "SUPPORTED_SOURCES",
    "Feature",
    "SemanticStyleProfile",
    "PromptUnit",
    "semanticize_style_profile",
    "build_semantic_style_profile",
    "rank_features",
    "deduplicate_features",
    "to_prompt_units",
]
