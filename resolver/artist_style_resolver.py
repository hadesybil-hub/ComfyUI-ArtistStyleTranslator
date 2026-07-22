"""Resolve semantic profiles using builtin, external, then fallback priority."""

from ..prompt_builder import build_semantic_profile_for_artist
from ..style_engine import SemanticStyleProfile
from ..providers.base_provider import SemanticProviderError
from ..providers.builtin_provider import BuiltinSemanticProvider
from ..providers.external_profile_adapter import adapt_external_profile
from ..providers.provider_contract import (
    ProviderExtensionContract,
    ProviderOutputValidationError,
    resolve_provider,
    validate_provider_output,
)


class ArtistStyleResolverError(SemanticProviderError):
    """Controlled failure raised for invalid resolver configuration."""


def _clean_artist_name(artist_name):
    try:
        return str(artist_name or "").strip()
    except Exception:
        return ""


def _fallback_profile():
    """Return the exact generic semantic fallback used by Prompt Builder."""
    return build_semantic_profile_for_artist("", "Standard").semantic_profile


class ArtistStyleResolver:
    """Resolve builtin profiles first, then optional injected external data.

    Contract providers return a SemanticStyleProfile or None. Legacy injected
    providers may remain callable or expose ``get_profile(name)`` and return a
    raw profile dictionary. Raw data always passes through the External Profile
    Adapter before it can become a SemanticStyleProfile.
    """

    def __init__(self, external_provider=None):
        self.external_provider = external_provider
        self._builtin_provider = BuiltinSemanticProvider()
        if external_provider is not None and not self._can_query_external(
            external_provider
        ):
            raise ArtistStyleResolverError(
                "external provider must implement the Contract, be callable, "
                "or expose get_profile()"
            )

    @staticmethod
    def _can_query_external(provider):
        if isinstance(provider, ProviderExtensionContract):
            return True
        return callable(provider) or callable(
            getattr(provider, "get_profile", None)
        )

    @staticmethod
    def _query_external(provider, artist_name):
        if isinstance(provider, ProviderExtensionContract):
            return resolve_provider(provider, artist_name)
        getter = getattr(provider, "get_profile", None)
        if callable(getter):
            return getter(artist_name)
        return provider(artist_name)

    def resolve(self, artist_name):
        """Return a SemanticStyleProfile using deterministic source priority."""
        clean_name = _clean_artist_name(artist_name)
        builtin = self._builtin_provider.try_get_profile(clean_name)
        if builtin is not None and builtin.features:
            return builtin

        if clean_name and self.external_provider is not None:
            try:
                external_data = self._query_external(
                    self.external_provider,
                    clean_name,
                )
            except ProviderOutputValidationError:
                raise
            except Exception:
                external_data = None
            if external_data is not None:
                if isinstance(external_data, SemanticStyleProfile):
                    return validate_provider_output(external_data)
                return adapt_external_profile(external_data)

        return _fallback_profile()


def resolve_artist_style(artist_name, external_provider=None):
    """Convenience wrapper around ArtistStyleResolver.resolve()."""
    return ArtistStyleResolver(external_provider).resolve(artist_name)


__all__ = [
    "ArtistStyleResolver",
    "ArtistStyleResolverError",
    "resolve_artist_style",
]
