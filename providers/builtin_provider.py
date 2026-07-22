"""Adapter exposing the existing built-in database through one contract."""

from ..artist_database import get_artist, list_artists as list_builtin_artists
from ..style_engine import semanticize_style_profile
from .base_provider import SemanticProvider, SemanticProviderError


class BuiltinSemanticProvider(SemanticProvider):
    """Create semantic profiles from existing built-in database records."""

    provider_name = "builtin"
    provider_version = "1.6.2"
    description = "Built-in curated artistic style semantic profiles."
    priority = 100
    source = "builtin"
    generated_by = "artist_database"

    def supports(self, artist_name: str) -> bool:
        return get_artist(artist_name) is not None

    def list_artists(self) -> list[str]:
        return list_builtin_artists()

    def get_profile(self, artist_name: str, external_data=None):
        entry = get_artist(artist_name)
        if entry is None:
            raise SemanticProviderError("artist is not present in the built-in database")
        return semanticize_style_profile(
            entry.get("style_profile", {}),
            source=self.source,
            confidence=0.95,
            evidence=("builtin structured style profile",),
            generated_by=self.generated_by,
        )


__all__ = ["BuiltinSemanticProvider"]
