"""Validate structured external data and create semantic style profiles."""

from collections.abc import Mapping
import json
import math

from ..style_engine import (
    Feature,
    SemanticStyleProfile,
    deduplicate_features,
    rank_features,
)
from .base_provider import SemanticProviderError


EXTERNAL_SEMANTIC_SCHEMA = {
    "type": "object",
    "required": ["features"],
    "additionalProperties": False,
    "properties": {
        "artist": {"type": "string"},
        "source": {"type": "string", "minLength": 1},
        "generated_by": {"type": "string", "minLength": 1},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "evidence": {
            "oneOf": [
                {"type": "string"},
                {"type": "array", "items": {"type": "string"}},
            ]
        },
        "features": {
            "type": "array",
            "minItems": 1,
            "maxItems": 128,
            "items": {
                "type": "object",
                "required": ["category", "value"],
                "additionalProperties": False,
                "properties": {
                    "category": {"type": "string", "minLength": 1},
                    "value": {"type": "string", "minLength": 1},
                    "priority": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "source": {"type": "string", "minLength": 1},
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "evidence": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    "generated_by": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}

_TOP_LEVEL_KEYS = {
    "artist",
    "source",
    "generated_by",
    "confidence",
    "evidence",
    "features",
}
_FEATURE_KEYS = {
    "category",
    "value",
    "priority",
    "source",
    "confidence",
    "evidence",
    "generated_by",
}


class ExternalDataValidationError(SemanticProviderError):
    """Raised when structured external semantic data is invalid."""


def _validation_error(message):
    raise ExternalDataValidationError(message)


def _number(value, field_name, default):
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _validation_error(f"{field_name} must be a number")
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        _validation_error(f"{field_name} must be between 0 and 1")
    return result


def _text(value, field_name, *, required=False):
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        _validation_error(f"{field_name} must be a string")
    result = value.strip()
    if required and not result:
        _validation_error(f"{field_name} must not be empty")
    return result


def _evidence(value, field_name):
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if not isinstance(value, list):
        _validation_error(f"{field_name} must be a string or string array")
    result = []
    for index, item in enumerate(value):
        result.append(_text(item, f"{field_name}[{index}]", required=True))
    return tuple(result)


def validate_external_semantic_data(data):
    """Parse JSON-compatible data and validate its semantic feature schema."""
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExternalDataValidationError("data is not UTF-8") from exc
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ExternalDataValidationError("data is not valid JSON") from exc
    if not isinstance(data, Mapping):
        _validation_error("data root must be an object")

    extra_keys = set(data) - _TOP_LEVEL_KEYS
    if extra_keys:
        _validation_error(f"unexpected data fields: {sorted(extra_keys)}")
    if "features" not in data:
        _validation_error("data.features is required")
    features = data["features"]
    if not isinstance(features, list) or not 1 <= len(features) <= 128:
        _validation_error("data.features must contain 1 to 128 items")

    default_confidence = _number(data.get("confidence"), "data.confidence", 0.8)
    normalized = {
        "artist": _text(data.get("artist"), "data.artist"),
        "source": _text(data.get("source"), "data.source"),
        "generated_by": _text(data.get("generated_by"), "data.generated_by"),
        "confidence": default_confidence,
        "evidence": _evidence(data.get("evidence"), "data.evidence"),
        "features": [],
    }

    for index, item in enumerate(features):
        if not isinstance(item, Mapping):
            _validation_error(f"data.features[{index}] must be an object")
        extra_feature_keys = set(item) - _FEATURE_KEYS
        if extra_feature_keys:
            _validation_error(
                f"unexpected feature fields at index {index}: "
                f"{sorted(extra_feature_keys)}"
            )
        normalized["features"].append(
            {
                "category": _text(
                    item.get("category"),
                    f"data.features[{index}].category",
                    required=True,
                ),
                "value": _text(
                    item.get("value"),
                    f"data.features[{index}].value",
                    required=True,
                ),
                "priority": _number(
                    item.get("priority"),
                    f"data.features[{index}].priority",
                    0.5,
                ),
                "source": _text(
                    item.get("source"),
                    f"data.features[{index}].source",
                ),
                "confidence": _number(
                    item.get("confidence"),
                    f"data.features[{index}].confidence",
                    default_confidence,
                ),
                "evidence": _evidence(
                    item.get("evidence"),
                    f"data.features[{index}].evidence",
                ),
                "generated_by": _text(
                    item.get("generated_by"),
                    f"data.features[{index}].generated_by",
                ),
            }
        )
    return normalized


def semantic_profile_from_external_data(
    data,
    *,
    source="user",
    generated_by="external_provider",
):
    """Convert validated structured semantic data to SemanticStyleProfile."""
    default_source = _text(source, "source", required=True)
    default_generator = _text(generated_by, "generated_by", required=True)
    payload = validate_external_semantic_data(data)
    profile_source = payload["source"] or default_source
    profile_generator = payload["generated_by"] or default_generator
    profile_evidence = payload["evidence"]

    features = tuple(
        Feature(
            category=item["category"],
            value=item["value"],
            priority=item["priority"],
            source=item["source"] or profile_source,
            confidence=item["confidence"],
            evidence=item["evidence"] or profile_evidence,
            generated_by=item["generated_by"] or profile_generator,
        )
        for item in payload["features"]
    )
    prepared = rank_features(deduplicate_features(features))
    return SemanticStyleProfile(
        features=prepared,
        source=profile_source,
        confidence=payload["confidence"],
        evidence=profile_evidence,
        generated_by=profile_generator,
    )


__all__ = [
    "EXTERNAL_SEMANTIC_SCHEMA",
    "ExternalDataValidationError",
    "validate_external_semantic_data",
    "semantic_profile_from_external_data",
]
