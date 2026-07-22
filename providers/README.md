# Provider Extension Contract

V1.6.2 defines a stable boundary between semantic data sources and the style
engine. Providers produce structured artistic-style semantics; they do not
produce prompts and must not depend on ComfyUI.

```text
builtin / external / ollama / web / user
                    |
                    v
        Provider Extension Contract
                    |
                    v
          SemanticStyleProfile
                    |
                    v
              Style Engine
                    |
                    v
             Prompt Builder
```

## Implementing a provider

Subclass `ProviderExtensionContract` and implement:

```python
from package.providers import ProviderExtensionContract


class MySemanticProvider(ProviderExtensionContract):
    provider_name = "my-semantic-provider"
    provider_version = "1.0.0"
    description = "Provides curated semantic style profiles."
    priority = 10

    def supports(self, artist_name: str) -> bool:
        ...

    def get_profile(self, artist_name: str):
        # Return a validated SemanticStyleProfile, or None when there is no
        # profile for this artist.
        ...

    def list_artists(self) -> list[str]:
        # Return canonical discoverable names, or [] when unavailable.
        ...
```

`get_profile()` is the single provider-specific query operation. The Contract
keeps `resolve()` as a compatibility wrapper that normalizes the artist name,
calls `supports()`, delegates to `get_profile()`, and validates the result.

Callers should invoke providers through `resolve_provider(provider, name)`.
This normalizes surrounding whitespace, converts unexpected provider failures
to `ProviderContractError`, and validates every non-None result. Third-party
providers must not return dictionaries or final prompt strings. Structured
external dictionaries should first be converted with
`adapt_external_profile()`.

## Input and output

Input:

- `artist_name`: a non-empty string. The contract gateway strips surrounding
  whitespace before calling the provider.

Output:

- `SemanticStyleProfile`: a matched semantic profile.
- `None`: no match. This is a normal result in a multi-provider resolution
  chain, not an invalid profile.

Use `validate_provider_output(profile)` when a profile is required. It rejects
`None`, non-profile values, empty feature collections, malformed features, and
missing provenance metadata.

## Provider information and capabilities

Every provider exposes four basic information fields:

- `provider_name`: stable non-empty provider identifier
- `provider_version`: provider implementation version
- `description`: short human-readable purpose
- `priority`: integer ordering hint for future resolver orchestration

The base Contract supplies conservative defaults so existing V1.6.1
`SemanticProvider` implementations remain instantiable until their Phase 3
migration. It also supplies default `supports()` and `list_artists()` behavior:
legacy providers may attempt any non-empty name and expose no discovery list.
Concrete providers can override both without changing the query contract.

## Required metadata

Both the profile and every `Feature` require:

- `source`: one of `builtin`, `external`, `ollama`, `web`, or `user`
- `confidence`: a finite number from `0.0` through `1.0`
- `evidence`: a non-empty tuple of non-empty strings
- `generated_by`: a non-empty producer identifier

Every feature also requires non-empty `category` and `value` fields. Validation
preserves metadata exactly; it does not rewrite provenance or semantic values.

## Existing providers and adapters

`SemanticProvider` keeps the legacy `get_profile()` interface and delegates
its existing `resolve()` entry to the extension contract. Therefore
`BuiltinSemanticProvider` remains compatible without changing its existing
lookup behavior.

`BuiltinSemanticProvider` publishes concrete V1.6.2 provider information,
checks support through the existing artist database, and delegates discovery
to `artist_database.list_artists()`. It does not maintain a second artist list.

`ExternalSemanticProvider` also publishes concrete provider information and
keeps its existing caller-supplied structured-data conversion. It can attempt
non-empty artist names, but its default discovery list is empty because it has
no enumerable data source.

`adapt_external_profile()` validates external structured data, converts it to
`Feature` objects, assigns explicit `external` provenance, and validates the
result against this contract before returning it.

The contract contains no network, HTTP, subprocess, model-client, frontend, or
prompt-generation implementation. Future Ollama, web, and user sources must
live outside this boundary and return the same semantic representation.
