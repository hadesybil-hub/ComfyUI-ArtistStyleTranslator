"""Provider-neutral contract for semantic style profile sources."""

from abc import ABC, abstractmethod

from ..style_engine import SemanticStyleProfile


class SemanticProviderError(RuntimeError):
    """Base class for controlled semantic-provider failures."""


class SemanticProvider(ABC):
    """Abstract source of provider-neutral semantic style profiles."""

    @abstractmethod
    def get_profile(
        self,
        artist_name: str,
        external_data=None,
    ) -> SemanticStyleProfile:
        """Return a semantic profile or raise SemanticProviderError."""

    def try_get_profile(self, artist_name: str, external_data=None):
        """Return None instead of propagating a controlled provider failure."""
        try:
            return self.get_profile(artist_name, external_data)
        except SemanticProviderError:
            return None


__all__ = ["SemanticProvider", "SemanticProviderError"]
