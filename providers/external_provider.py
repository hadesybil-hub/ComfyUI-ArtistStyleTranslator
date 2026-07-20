"""Generic provider for already-available structured semantic data."""

from .base_provider import SemanticProvider, SemanticProviderError
from .external_adapter import semantic_profile_from_external_data


class ExternalSemanticProvider(SemanticProvider):
    """Adapt structured data supplied by Ollama, web, user, or future tools."""

    def __init__(self, *, source="user", generated_by="external_provider"):
        self.source = self._required_text(source, "source")
        self.generated_by = self._required_text(generated_by, "generated_by")

    @staticmethod
    def _required_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise SemanticProviderError(f"{field_name} must be a non-empty string")
        return value.strip()

    def get_profile(self, artist_name: str, external_data=None):
        self._required_text(artist_name, "artist_name")
        if external_data is None:
            raise SemanticProviderError("external semantic data is required")
        return semantic_profile_from_external_data(
            external_data,
            source=self.source,
            generated_by=self.generated_by,
        )


__all__ = ["ExternalSemanticProvider"]
