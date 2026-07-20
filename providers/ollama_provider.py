"""Backward-compatible Ollama semantic adapter with no client or network code."""

from collections.abc import Callable

from .base_provider import SemanticProviderError
from .external_adapter import (
    EXTERNAL_SEMANTIC_SCHEMA,
    ExternalDataValidationError,
    validate_external_semantic_data,
)
from .external_provider import ExternalSemanticProvider


OLLAMA_RESPONSE_SCHEMA = EXTERNAL_SEMANTIC_SCHEMA
OllamaProviderError = SemanticProviderError
OllamaResponseValidationError = ExternalDataValidationError
validate_ollama_response = validate_external_semantic_data


class OllamaProviderUnavailableError(SemanticProviderError):
    """Raised when neither structured data nor a response loader is supplied."""


class OllamaProvider(ExternalSemanticProvider):
    """Compatibility adapter for externally supplied Ollama semantic JSON.

    It intentionally contains no Ollama API client. Existing ecosystems can
    supply structured data directly, while V1.5.0 callers may keep injecting a
    response loader.
    """

    source = "ollama"
    generated_by = "ollama"

    def __init__(self, response_loader: Callable[[str], object] | None = None):
        super().__init__(source=self.source, generated_by=self.generated_by)
        self._response_loader = response_loader

    def get_profile(self, artist_name: str, external_data=None):
        artist = self._required_text(artist_name, "artist_name")
        if external_data is None:
            if self._response_loader is None:
                raise OllamaProviderUnavailableError(
                    "no Ollama response loader or external data is configured"
                )
            try:
                external_data = self._response_loader(artist)
            except SemanticProviderError:
                raise
            except Exception as exc:
                raise SemanticProviderError("Ollama response loader failed") from exc
        return super().get_profile(artist, external_data)

    def get_semantic_profile(self, artist_name: str):
        """V1.5.0-compatible name for loader-based profile conversion."""
        return self.get_profile(artist_name)

    def try_get_semantic_profile(self, artist_name: str):
        """V1.5.0-compatible safe loader-based profile conversion."""
        return self.try_get_profile(artist_name)


__all__ = [
    "OLLAMA_RESPONSE_SCHEMA",
    "OllamaProvider",
    "OllamaProviderError",
    "OllamaProviderUnavailableError",
    "OllamaResponseValidationError",
    "validate_ollama_response",
]
