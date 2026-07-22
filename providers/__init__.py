"""Provider-neutral semantic profile interfaces and adapters."""

from .provider_contract import (
    SUPPORTED_PROVIDER_SOURCES,
    ProviderContractError,
    ProviderExtensionContract,
    ProviderOutputValidationError,
    resolve_provider,
    validate_provider_output,
)
from .base_provider import SemanticProvider, SemanticProviderError
from .builtin_provider import BuiltinSemanticProvider
from .external_adapter import (
    EXTERNAL_SEMANTIC_SCHEMA,
    ExternalDataValidationError,
    semantic_profile_from_external_data,
    validate_external_semantic_data,
)
from .external_provider import ExternalSemanticProvider
from .external_profile_adapter import (
    ExternalProfileAdapter,
    ExternalProfileAdapterError,
    adapt_external_profile,
)
from .ollama_provider import (
    OLLAMA_RESPONSE_SCHEMA,
    OllamaProvider,
    OllamaProviderError,
    OllamaProviderUnavailableError,
    OllamaResponseValidationError,
    validate_ollama_response,
)

__all__ = [
    "SUPPORTED_PROVIDER_SOURCES",
    "ProviderContractError",
    "ProviderExtensionContract",
    "ProviderOutputValidationError",
    "resolve_provider",
    "validate_provider_output",
    "SemanticProvider",
    "SemanticProviderError",
    "BuiltinSemanticProvider",
    "ExternalSemanticProvider",
    "ExternalProfileAdapter",
    "ExternalProfileAdapterError",
    "adapt_external_profile",
    "EXTERNAL_SEMANTIC_SCHEMA",
    "ExternalDataValidationError",
    "semantic_profile_from_external_data",
    "validate_external_semantic_data",
    "OLLAMA_RESPONSE_SCHEMA",
    "OllamaProvider",
    "OllamaProviderError",
    "OllamaProviderUnavailableError",
    "OllamaResponseValidationError",
    "validate_ollama_response",
]
