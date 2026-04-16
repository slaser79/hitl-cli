---
title: "hitl-cli"
type: product
products: [hitl-cli]
last_updated: 2026-04-14
sources:
  - config/empire.yaml
cross_refs:
  - ../index.md
  - ../products/ai_assistant.md
---

# hitl-cli

SDK and reference client for interacting with the HitL (Human-in-the-Loop) platform.

## Architecture Overview

A library and command-line interface designed to facilitate integration with the core HitL API. It provides high-level abstractions for common tasks like creating tasks, checking status, and responding to HitL requests.

### Core Components

- **Python SDK**: Typed client for programmatic access to the HitL API.
- **CLI Tool**: Direct command-line access to platform features (tasks, missions, status).
- **Authentication Wrapper**: Manages JWTs and OAuth flow for secure API calls.
- **Reference Implementation**: Serves as the "gold standard" for other client integrations.

## Tech Stack

- **Language**: Python 3.10+
- **API**: REST via `httpx`.
- **CLI Framework**: `typer` or `click`.
- **Distribution**: PyPI package and standalone executable.

## Key Patterns

- **Synchronous and Asynchronous**: Support both `async` and blocking call patterns for maximum flexibility.
- **Rich Logging**: Verbose logging by default for debugging agent-system interactions.
- **Fail-Fast**: Immediate validation of API inputs to prevent round-trip errors.

## Known Gotchas

- **Token Expiry**: Be aware of JWT expiration; implementing a robust refresh mechanism is critical for long-running scripts.
- **Rate Limits**: CLI calls are subject to API rate limiting; implement exponential backoff where necessary.
