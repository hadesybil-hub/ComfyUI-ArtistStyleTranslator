"""Formatting helpers for previewing semantic style profiles.

This module is intentionally presentation-only. It consumes the provider-neutral
SemanticStyleProfile produced by the style engine and does not resolve artists,
build prompts, adapt models, or call providers.
"""

import json

from .style_engine import Feature, SemanticStyleProfile


SUPPORTED_FORMATS = ("text", "dict", "json")


def _require_profile(profile):
    if not isinstance(profile, SemanticStyleProfile):
        raise TypeError("profile must be a SemanticStyleProfile")
    return profile


def _feature_to_dict(feature):
    if not isinstance(feature, Feature):
        raise TypeError("profile features must be Feature objects")
    return {
        "category": feature.category,
        "value": feature.value,
        "priority": feature.priority,
        "source": feature.source,
        "confidence": feature.confidence,
        "evidence": list(feature.evidence),
        "generated_by": feature.generated_by,
    }


def profile_to_dict(profile):
    """Return a JSON-compatible preview dictionary without changing semantics."""
    profile = _require_profile(profile)
    return {
        "source": profile.source,
        "confidence": profile.confidence,
        "evidence": list(profile.evidence),
        "generated_by": profile.generated_by,
        "features": [_feature_to_dict(feature) for feature in profile.features],
    }


def profile_to_text(profile):
    """Return a stable human-readable preview of a semantic profile."""
    data = profile_to_dict(profile)
    lines = [
        "Semantic Style Profile",
        f"source: {data['source']}",
        f"confidence: {data['confidence']:.3f}",
        f"generated_by: {data['generated_by']}",
    ]

    if data["evidence"]:
        lines.append(f"evidence: {'; '.join(data['evidence'])}")

    lines.append("features:")
    if not data["features"]:
        lines.append("  (none)")
        return "\n".join(lines)

    for feature in data["features"]:
        lines.append(f"  - [{feature['category']}] {feature['value']}")
        lines.append(
            "    "
            f"priority={feature['priority']:.3f}, "
            f"confidence={feature['confidence']:.3f}, "
            f"source={feature['source']}, "
            f"generated_by={feature['generated_by']}"
        )
        if feature["evidence"]:
            lines.append(f"    evidence: {'; '.join(feature['evidence'])}")

    return "\n".join(lines)


def profile_to_json(profile, *, indent=2):
    """Return a deterministic UTF-8 JSON preview string."""
    return json.dumps(
        profile_to_dict(profile),
        ensure_ascii=False,
        indent=indent,
        separators=(",", ": "),
    )


def format_profile(profile, output_format="text"):
    """Format a semantic profile as text, dict, or JSON."""
    normalized_format = str(output_format or "").strip().casefold()
    if normalized_format == "text":
        return profile_to_text(profile)
    if normalized_format == "dict":
        return profile_to_dict(profile)
    if normalized_format == "json":
        return profile_to_json(profile)
    raise ValueError(
        f"Unsupported profile format: {output_format!r}. "
        f"Expected one of {SUPPORTED_FORMATS}."
    )
