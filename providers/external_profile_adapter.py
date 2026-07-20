"""Convert validated external semantic dictionaries into style profiles."""

from collections.abc import Mapping

from ..style_engine import (
    Feature,
    SemanticStyleProfile,
    deduplicate_features,
    rank_features,
)
from .base_provider import SemanticProviderError
from .external_adapter import (
    ExternalDataValidationError,
    validate_external_semantic_data,
)


class ExternalProfileAdapterError(SemanticProviderError):
    """Controlled failure raised for invalid external profile data."""


def adapt_external_profile(profile_data):
    """Return a SemanticStyleProfile with external provenance metadata."""
    if not isinstance(profile_data, Mapping):
        raise ExternalProfileAdapterError(
            "external profile must be a dictionary"
        )

    try:
        payload = validate_external_semantic_data(profile_data)
    except ExternalDataValidationError as exc:
        raise ExternalProfileAdapterError(str(exc)) from exc

    profile_evidence = payload["evidence"]
    features = tuple(
        Feature(
            category=item["category"],
            value=item["value"],
            priority=item["priority"],
            source="external",
            confidence=item["confidence"],
            evidence=item["evidence"] or profile_evidence,
            generated_by="external",
        )
        for item in payload["features"]
    )
    prepared = rank_features(deduplicate_features(features))
    return SemanticStyleProfile(
        features=prepared,
        source="external",
        confidence=payload["confidence"],
        evidence=profile_evidence,
        generated_by="external",
    )


class ExternalProfileAdapter:
    """Small object-oriented facade for external profile conversion."""

    @staticmethod
    def convert(profile_data):
        return adapt_external_profile(profile_data)


__all__ = [
    "ExternalProfileAdapter",
    "ExternalProfileAdapterError",
    "adapt_external_profile",
]
