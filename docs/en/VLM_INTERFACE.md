# VLM Interface

Last updated: 2026-05-28

## Purpose

This document records the first provider-neutral VLM interface for the View-Aware Graph project.

The interface supports only:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

It does not implement downstream Cypher generation, Neo4j retrieval, graph matching, localization, or mapping.

## Current Scope

The first Phase 5 implementation defines provider-neutral contracts and settings.

Implemented:

- `VLMRequest`
- `VLMResponse`
- `VLMAdapter` protocol
- `VLMSettings`
- `RetryPolicy`
- `VLMFailure`
- `VLMAdapterError`
- TOML config loading with environment overrides
- raw VLM response path policy under `data/interim/vlm_raw/`
- processed graph output path policy under `data/processed/view_graphs/`
- structured failure reporting with retryability metadata
- concrete `OllamaAdapter` behind the provider-neutral adapter interface

Not implemented yet:

- hosted provider adapters
- CLI workflow
- retry execution loop inside concrete adapters
- automatic graph repair

## Configuration Policy

Repeatable defaults live in:

```text
configs/default.toml
```

Environment variables may override provider credentials and selected model:

```text
VLM_PROVIDER
VLM_MODEL
VLM_ENDPOINT
VLM_TIMEOUT_SECONDS
VLM_API_KEY
```

Core logic must not hard-code a provider, model, API key, or local absolute path.

Large local models can exceed the default request timeout while loading or
generating. `VLM_TIMEOUT_SECONDS` overrides the configured adapter timeout for
those runs.

## Output Path Policy

Raw provider responses should be written under:

```text
data/interim/vlm_raw/
```

Validated or repaired graph JSON outputs should be written under:

```text
data/processed/view_graphs/
```

Both directories are local work areas and ignored by Git.

## Retry And Failure Reporting

`RetryPolicy` defines how many retries a concrete adapter may attempt.

`max_retries` counts retries after the first attempt, so total attempts are:

```text
max_retries + 1
```

The first retryable error categories are:

- `timeout`
- `connection_error`
- `rate_limited`
- `server_error`

Schema mismatches, invalid JSON, and semantic graph quality failures are not adapter-level retryable failures by default. They should be handled by parsing, validation, repair, or evaluation logic.

`VLMFailure` records:

- provider
- model
- image id
- error type
- message
- attempts
- retryable flag
- optional raw response path
- optional metadata

## Next Implementation Step

After Phase 5 contracts and Phase 6 parsing/validation helpers are stable, the project can add a concrete local Ollama adapter or a minimal CLI workflow.

The Ollama adapter should remain behind `VLMAdapter` so later paid or local providers can be swapped without changing graph parsing and validation code.

## Ollama Adapter

`OllamaAdapter` targets Ollama's local `/api/generate` endpoint for single-image prompt runs.

It:

- base64-encodes the input image
- sends `stream: false`
- requests `format: "json"`
- passes `temperature` through `options`
- extracts the nested Ollama `response` field into `VLMResponse.graph_text`
- reports adapter failures through `VLMAdapterError` and `VLMFailure`

Unit tests use an injected transport and do not call the local Ollama server.

Real Ollama execution remains a project-owner runtime action.
