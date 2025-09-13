---
# HITL CLI - Human-in-the-Loop Command Line Interface

[![Python CI](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/hitl-cli/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A reference implementation of a command-line interface for Human-in-the-Loop (HITL) services. This CLI provides seamless integration with HITL backend services, enabling users to manage agents, send requests for human input, and handle authentication through OAuth 2.1 dynamic client registration.

## Features

- 🔐 OAuth 2.1 Authentication: Dynamic client registration with PKCE security
- ⚡ Zero-Config Auth: Dynamic client registration eliminates manual OAuth setup
- 🛡️ Enhanced Security: PKCE (Proof Key for Code Exchange) support for OAuth 2.1
- 🔒 End-to-End Encryption: Optional E2EE proxy mode for maximum privacy
- 🛡️ Cryptographic Guardian: Transparent encryption between agents and humans
- 🤖 Agent Management: Create, list, and rename AI agents with customizable names
- 💬 Human-in-the-Loop Requests: Send requests for human decisions with customizable choices
- 🔄 MCP Integration: Built-in support for Model Context Protocol (MCP) clients
- 📊 Request Tracking: Monitor request status and receive human responses
- 🔑 Secure Token Storage: Platform-specific secure credential storage with automatic refresh

## Installation

### Using Nix (Recommended)

If you have Nix installed, you can use the provided flake for a reproducible development environment:

# Enter the development shell
nix develop

# The virtual environment will be automatically activated
# Dependencies will be synced automatically
