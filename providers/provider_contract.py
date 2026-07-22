"""Stable extension boundary for semantic style profile providers.

Providers resolve artist names into provider-neutral semantic profiles.  This
module validates that boundary only; it performs no prompting, network access,
process execution, or ComfyUI integration.
"""

from abc import ABC, abstractmethod
import math

from ..style_engine import Feature, SemanticStyleProfile


SUPPORTED_PROVIDER_SOURCES = (
    "builtin",
    "external",
    "ollama",
    "web",
    "user",
)


class ProviderContractError(RuntimeError):
    """Base class for controlled provider-contract failures."""


class ProviderOutputValidationError(ProviderContractError):
    """Raised when a provider returns an invalid semantic profile."""


class ProviderExtensionContract(ABC):
    """Interface implemented by third-party semantic profile providers.

    ``get_profile`` is the one provider-specific query operation. ``resolve``
    remains the stable compatibility entry that checks support and validates
    every non-None result before it crosses the provider boundary.
    """

    provider_name = "semantic-provider"
    provider_version = "1.0"
    description = "Semantic style profile provider."
    priority = 0

    @abstractmethod
    def get_profile(self, artist_name: str) -> SemanticStyleProfile | None:
        """Return semantic data for one artist, or None when unavailable."""

    def supports(self, artist_name: str) -> bool:
        """Return whether this provider can attempt the artist lookup."""
        return True

    def list_artists(self) -> list[str]:
        """Return discoverable canonical names, or an empty list."""
        return []

    def resolve(self, artist_name: str) -> SemanticStyleProfile | None:
        """Resolve through get_profile() and validate the semantic result."""
        if not isinstance(artist_name, str) or not artist_name.strip():
            raise ProviderContractError(
                "artist_name must be a non-empty string"
            )
        clean_name = artist_name.strip()

        try:
            supported = self.supports(clean_name)
        except ProviderContractError:
            raise
        except Exception as exc:
            raise ProviderContractError("provider supports() failed") from exc
        if not isinstance(supported, bool):
            raise ProviderContractError("provider supports() must return bool")
        if not supported:
            return None

        try:
            profile = self.get_profile(clean_name)
        except ProviderContractError:
            return None
        except Exception as exc:
            raise ProviderContractError("provider get_profile() failed") from exc
        return validate_provider_output(profile, allow_none=True)


def _required_text(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ProviderOutputValidationError(
            f"{field_name} must be a non-empty string"
        )
    return value.strip()


def _confidence(value, field_name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProviderOutputValidationError(
            f"{field_name} must be a number between 0 and 1"
        )
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ProviderOutputValidationError(
            f"{field_name} must be a number between 0 and 1"
        )
    return score


def _required_evidence(value, field_name):
    if not isinstance(value, tuple) or not value:
        raise ProviderOutputValidationError(
            f"{field_name} must be a non-empty tuple of strings"
        )
    for index, item in enumerate(value):
        _required_text(item, f"{field_name}[{index}]")


def _validate_metadata(item, field_name):
    source = _required_text(item.source, f"{field_name}.source")
    if source not in SUPPORTED_PROVIDER_SOURCES:
        raise ProviderOutputValidationError(
            f"{field_name}.source must be one of "
            f"{SUPPORTED_PROVIDER_SOURCES}"
        )
    _confidence(item.confidence, f"{field_name}.confidence")
    _required_evidence(item.evidence, f"{field_name}.evidence")
    _required_text(item.generated_by, f"{field_name}.generated_by")


def validate_provider_output(
    profile,
    *,
    allow_none=False,
) -> SemanticStyleProfile | None:
    """Validate and return one provider result without changing metadata.

    ``allow_none`` is reserved for resolution chains, where no match is a
    valid outcome.  Direct validation rejects a missing profile by default.
    """
    if profile is None:
        if allow_none:
            return None
        raise ProviderOutputValidationError(
            "provider output is missing a semantic profile"
        )
    if not isinstance(profile, SemanticStyleProfile):
        raise ProviderOutputValidationError(
            "provider output must be a SemanticStyleProfile or None"
        )
    if not isinstance(profile.features, tuple) or not profile.features:
        raise ProviderOutputValidationError(
            "provider profile must contain at least one Feature"
        )

    _validate_metadata(profile, "profile")
    for index, feature in enumerate(profile.features):
        if not isinstance(feature, Feature):
            raise ProviderOutputValidationError(
                f"profile.features[{index}] must be a Feature"
            )
        _required_text(feature.category, f"profile.features[{index}].category")
        _required_text(feature.value, f"profile.features[{index}].value")
        _validate_metadata(feature, f"profile.features[{index}]")
    return profile


def _validate_provider_information(provider):
    for field_name in (
        "provider_name",
        "provider_version",
        "description",
    ):
        value = getattr(provider, field_name, None)
        if not isinstance(value, str) or not value.strip():
            raise ProviderContractError(
                f"provider {field_name} must be a non-empty string"
            )

    priority = getattr(provider, "priority", None)
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ProviderContractError("provider priority must be an integer")


def resolve_provider(
    provider: ProviderExtensionContract,
    artist_name: str,
) -> SemanticStyleProfile | None:
    """Call one extension provider and enforce its public contract."""
    if not isinstance(provider, ProviderExtensionContract):
        raise ProviderContractError(
            "provider must implement ProviderExtensionContract"
        )
    _validate_provider_information(provider)
    if not isinstance(artist_name, str) or not artist_name.strip():
        raise ProviderContractError("artist_name must be a non-empty string")

    clean_name = artist_name.strip()
    try:
        profile = provider.resolve(clean_name)
    except ProviderContractError:
        raise
    except Exception as exc:
        raise ProviderContractError("provider resolution failed") from exc
    return validate_provider_output(profile, allow_none=True)


__all__ = [
    "SUPPORTED_PROVIDER_SOURCES",
    "ProviderContractError",
    "ProviderOutputValidationError",
    "ProviderExtensionContract",
    "validate_provider_output",
    "resolve_provider",
]
