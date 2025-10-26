Title: GitHub - jlowin/fastmcp: 🚀 The fast, Pythonic way to build MCP servers and clients

URL Source: https://github.com/jlowin/fastmcp?tab=readme-ov-file

Markdown Content:
FastMCP v2 🚀
-------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#fastmcp-v2-)
**The fast, Pythonic way to build MCP servers and clients.**

_Made with ☕️ by [Prefect](https://www.prefect.io/)_

[![Image 1: Docs](https://camo.githubusercontent.com/4fc759e03096f1811d9e10de82f8abdcf2eaf8218aa14395b2bd848cd72829a9/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f63732d676f666173746d63702e636f6d2d626c7565)](https://gofastmcp.com/)[![Image 2: PyPI - Version](https://camo.githubusercontent.com/571af8b9c9cf7b99e371fe54614d2c2fabc3579c4ca8a6106d01fbba280d69d7/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f666173746d63702e737667)](https://pypi.org/project/fastmcp)[![Image 3: Tests](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml/badge.svg)](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml)[![Image 4: License](https://camo.githubusercontent.com/9eeb024ed9173dd272ded357cd6de7ec3d7e0b229045de94971f70c4e8f5e359/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f6a6c6f77696e2f666173746d63702e737667)](https://github.com/jlowin/fastmcp/blob/main/LICENSE)

[![Image 5: jlowin%2Ffastmcp | Trendshift](https://camo.githubusercontent.com/820d21df75e7cefe69c9321a491c7cd0d0f5c1d45cc3a1e1aa1bf6387732ceeb/68747470733a2f2f7472656e6473686966742e696f2f6170692f62616467652f7265706f7369746f726965732f3133323636)](https://trendshift.io/repositories/13266)

Note

#### Beyond the Protocol

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#beyond-the-protocol)
FastMCP is the standard framework for working with the Model Context Protocol. FastMCP 1.0 was incorporated into the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) in 2024.

This is FastMCP 2.0, the **actively maintained version** that provides a complete toolkit for working with the MCP ecosystem.

FastMCP 2.0 has a comprehensive set of features that go far beyond the core MCP specification, all in service of providing **the simplest path to production**. These include deployment, auth, clients, server proxying and composition, generating servers from REST APIs, dynamic tool rewriting, built-in testing tools, integrations, and more.

Ready to upgrade or get started? Follow the [installation instructions](https://gofastmcp.com/getting-started/installation), which include steps for upgrading from the official MCP SDK.

* * *

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a new, standardized way to provide context and tools to your LLMs, and FastMCP makes building MCP servers and clients simple and intuitive. Create tools, expose resources, define prompts, and connect components with clean, Pythonic code.

# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if  __name__  == "__main__":
    mcp.run()

Run the server locally:

fastmcp run server.py

### 📚 Documentation

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#-documentation)
FastMCP's complete documentation is available at **[gofastmcp.com](https://gofastmcp.com/)**, including detailed guides, API references, and advanced patterns. This readme provides only a high-level overview.

Documentation is also available in [llms.txt format](https://llmstxt.org/), which is a simple markdown standard that LLMs can consume easily.

There are two ways to access the LLM-friendly documentation:

*   [`llms.txt`](https://gofastmcp.com/llms.txt) is essentially a sitemap, listing all the pages in the documentation.
*   [`llms-full.txt`](https://gofastmcp.com/llms-full.txt) contains the entire documentation. Note this may exceed the context window of your LLM.

* * *

Table of Contents
-----------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#table-of-contents)
*   [What is MCP?](https://github.com/jlowin/fastmcp?tab=readme-ov-file#what-is-mcp)
*   [Why FastMCP?](https://github.com/jlowin/fastmcp?tab=readme-ov-file#why-fastmcp)
*   [Installation](https://github.com/jlowin/fastmcp?tab=readme-ov-file#installation)
*   [Core Concepts](https://github.com/jlowin/fastmcp?tab=readme-ov-file#core-concepts)
    *   [The `FastMCP` Server](https://github.com/jlowin/fastmcp?tab=readme-ov-file#the-fastmcp-server)
    *   [Tools](https://github.com/jlowin/fastmcp?tab=readme-ov-file#tools)
    *   [Resources & Templates](https://github.com/jlowin/fastmcp?tab=readme-ov-file#resources--templates)
    *   [Prompts](https://github.com/jlowin/fastmcp?tab=readme-ov-file#prompts)
    *   [Context](https://github.com/jlowin/fastmcp?tab=readme-ov-file#context)
    *   [MCP Clients](https://github.com/jlowin/fastmcp?tab=readme-ov-file#mcp-clients)

*   [Advanced Features](https://github.com/jlowin/fastmcp?tab=readme-ov-file#advanced-features)
    *   [Proxy Servers](https://github.com/jlowin/fastmcp?tab=readme-ov-file#proxy-servers)
    *   [Composing MCP Servers](https://github.com/jlowin/fastmcp?tab=readme-ov-file#composing-mcp-servers)
    *   [OpenAPI & FastAPI Generation](https://github.com/jlowin/fastmcp?tab=readme-ov-file#openapi--fastapi-generation)
    *   [Authentication & Security](https://github.com/jlowin/fastmcp?tab=readme-ov-file#authentication--security)

*   [Running Your Server](https://github.com/jlowin/fastmcp?tab=readme-ov-file#running-your-server)
*   [Contributing](https://github.com/jlowin/fastmcp?tab=readme-ov-file#contributing)
    *   [Prerequisites](https://github.com/jlowin/fastmcp?tab=readme-ov-file#prerequisites)
    *   [Setup](https://github.com/jlowin/fastmcp?tab=readme-ov-file#setup)
    *   [Unit Tests](https://github.com/jlowin/fastmcp?tab=readme-ov-file#unit-tests)
    *   [Static Checks](https://github.com/jlowin/fastmcp?tab=readme-ov-file#static-checks)
    *   [Pull Requests](https://github.com/jlowin/fastmcp?tab=readme-ov-file#pull-requests)

* * *

What is MCP?
------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#what-is-mcp)
The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. It is often described as "the USB-C port for AI", providing a uniform way to connect LLMs to resources they can use. It may be easier to think of it as an API, but specifically designed for LLM interactions. MCP servers can:

*   Expose data through **Resources** (think of these sort of like GET endpoints; they are used to load information into the LLM's context)
*   Provide functionality through **Tools** (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
*   Define interaction patterns through **Prompts** (reusable templates for LLM interactions)
*   And more!

FastMCP provides a high-level, Pythonic interface for building, managing, and interacting with these servers.

Why FastMCP?
------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#why-fastmcp)
The MCP protocol is powerful but implementing it involves a lot of boilerplate - server setup, protocol handlers, content types, error management. FastMCP handles all the complex protocol details and server management, so you can focus on building great tools. It's designed to be high-level and Pythonic; in most cases, decorating a function is all you need.

FastMCP 2.0 has evolved into a comprehensive platform that goes far beyond basic protocol implementation. While 1.0 provided server-building capabilities (and is now part of the official MCP SDK), 2.0 offers a complete ecosystem including client libraries, authentication systems, deployment tools, integrations with major AI platforms, testing frameworks, and production-ready infrastructure patterns.

FastMCP aims to be:

🚀 **Fast:** High-level interface means less code and faster development

🍀 **Simple:** Build MCP servers with minimal boilerplate

🐍 **Pythonic:** Feels natural to Python developers

🔍 **Complete:** A comprehensive platform for all MCP use cases, from dev to prod

Installation
------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#installation)
We recommend installing FastMCP with [uv](https://docs.astral.sh/uv/):

uv pip install fastmcp

For full installation instructions, including verification, upgrading from the official MCPSDK, and developer setup, see the [**Installation Guide**](https://gofastmcp.com/getting-started/installation).

Core Concepts
-------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#core-concepts)
These are the building blocks for creating MCP servers and clients with FastMCP.

### The `FastMCP` Server

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#the-fastmcp-server)
The central object representing your MCP application. It holds your tools, resources, and prompts, manages connections, and can be configured with settings like authentication.

from fastmcp import FastMCP

# Create a server instance
mcp = FastMCP(name="MyAssistantServer")

Learn more in the [**FastMCP Server Documentation**](https://gofastmcp.com/servers/fastmcp).

### Tools

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#tools)
Tools allow LLMs to perform actions by executing your Python functions (sync or async). Ideal for computations, API calls, or side effects (like `POST`/`PUT`). FastMCP handles schema generation from type hints and docstrings. Tools can return various types, including text, JSON-serializable objects, and even images or audio aided by the FastMCP media helper classes.

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

Learn more in the [**Tools Documentation**](https://gofastmcp.com/servers/tools).

### Resources & Templates

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#resources--templates)
Resources expose read-only data sources (like `GET` requests). Use `@mcp.resource("your://uri")`. Use `{placeholders}` in the URI to create dynamic templates that accept parameters, allowing clients to request specific data subsets.

# Static resource
@mcp.resource("config://version")
def get_version(): 
    return "2.0.1"

# Dynamic resource template
@mcp.resource("users://{user_id}/profile")
def get_profile(user_id: int):
    # Fetch profile for user_id...
    return {"name": f"User {user_id}", "status": "active"}

Learn more in the [**Resources & Templates Documentation**](https://gofastmcp.com/servers/resources).

### Prompts

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#prompts)
Prompts define reusable message templates to guide LLM interactions. Decorate functions with `@mcp.prompt`. Return strings or `Message` objects.

@mcp.prompt
def summarize_request(text: str) -> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\n\n{text}"

Learn more in the [**Prompts Documentation**](https://gofastmcp.com/servers/prompts).

### Context

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#context)
Access MCP session capabilities within your tools, resources, or prompts by adding a `ctx: Context` parameter. Context provides methods for:

*   **Logging:** Log messages to MCP clients with `ctx.info()`, `ctx.error()`, etc.
*   **LLM Sampling:** Use `ctx.sample()` to request completions from the client's LLM.
*   **HTTP Request:** Use `ctx.http_request()` to make HTTP requests to other servers.
*   **Resource Access:** Use `ctx.read_resource()` to access resources on the server
*   **Progress Reporting:** Use `ctx.report_progress()` to report progress to the client.
*   and more...

To access the context, add a parameter annotated as `Context` to any mcp-decorated function. FastMCP will automatically inject the correct context object when the function is called.

from fastmcp import FastMCP, Context

mcp = FastMCP("My MCP Server")

@mcp.tool
async def process_data(uri: str, ctx: Context):
    # Log a message to the client
    await ctx.info(f"Processing {uri}...")

    # Read a resource from the server
    data = await ctx.read_resource(uri)

    # Ask client LLM to summarize the data
    summary = await ctx.sample(f"Summarize: {data.content[:500]}")

    # Return the summary
    return summary.text

Learn more in the [**Context Documentation**](https://gofastmcp.com/servers/context).

### MCP Clients

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#mcp-clients)
Interact with _any_ MCP server programmatically using the `fastmcp.Client`. It supports various transports (Stdio, SSE, In-Memory) and often auto-detects the correct one. The client can also handle advanced patterns like server-initiated **LLM sampling requests** if you provide an appropriate handler.

Critically, the client allows for efficient **in-memory testing** of your servers by connecting directly to a `FastMCP` server instance via the `FastMCPTransport`, eliminating the need for process management or network calls during tests.

from fastmcp import Client

async def main():
    # Connect via stdio to a local script
    async with Client("my_server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.content[0].text}")

    # Connect via SSE
    async with Client("http://localhost:8000/sse") as client:
        # ... use the client
        pass

To use clients to test servers, use the following pattern:

from fastmcp import FastMCP, Client

mcp = FastMCP("My MCP Server")

async def main():
    # Connect via in-memory transport
    async with Client(mcp) as client:
        # ... use the client

FastMCP also supports connecting to multiple servers through a single unified client using the standard MCP configuration format:

from fastmcp import Client

# Standard MCP configuration with multiple servers
config = {
    "mcpServers": {
        "weather": {"url": "https://weather-api.example.com/mcp"},
        "assistant": {"command": "python", "args": ["./assistant_server.py"]}
    }
}

# Create a client that connects to all servers
client = Client(config)

async def main():
    async with client:
        # Access tools and resources with server prefixes
        forecast = await client.call_tool("weather_get_forecast", {"city": "London"})
        answer = await client.call_tool("assistant_answer_question", {"query": "What is MCP?"})

Learn more in the [**Client Documentation**](https://gofastmcp.com/clients/client) and [**Transports Documentation**](https://gofastmcp.com/clients/transports).

Advanced Features
-----------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#advanced-features)
FastMCP introduces powerful ways to structure and deploy your MCP applications.

### Proxy Servers

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#proxy-servers)
Create a FastMCP server that acts as an intermediary for another local or remote MCP server using `FastMCP.as_proxy()`. This is especially useful for bridging transports (e.g., remote SSE to local Stdio) or adding a layer of logic to a server you don't control.

Learn more in the [**Proxying Documentation**](https://gofastmcp.com/patterns/proxy).

### Composing MCP Servers

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#composing-mcp-servers)
Build modular applications by mounting multiple `FastMCP` instances onto a parent server using `mcp.mount()` (live link) or `mcp.import_server()` (static copy).

Learn more in the [**Composition Documentation**](https://gofastmcp.com/patterns/composition).

### OpenAPI & FastAPI Generation

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#openapi--fastapi-generation)
Automatically generate FastMCP servers from existing OpenAPI specifications (`FastMCP.from_openapi()`) or FastAPI applications (`FastMCP.from_fastapi()`), instantly bringing your web APIs to the MCP ecosystem.

Learn more: [**OpenAPI Integration**](https://gofastmcp.com/integrations/openapi) | [**FastAPI Integration**](https://gofastmcp.com/integrations/fastapi).

### Authentication & Security

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#authentication--security)
FastMCP provides built-in authentication support to secure both your MCP servers and clients in production environments. Protect your server endpoints from unauthorized access and authenticate your clients against secured MCP servers using industry-standard protocols.

*   **Server Protection**: Secure your FastMCP server endpoints with configurable authentication providers
*   **Client Authentication**: Connect to authenticated MCP servers with automatic credential management
*   **Production Ready**: Support for common authentication patterns used in enterprise environments

Learn more in the **Authentication Documentation** for [servers](https://gofastmcp.com/servers/auth) and [clients](https://gofastmcp.com/clients/auth).

Running Your Server
-------------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#running-your-server)
The main way to run a FastMCP server is by calling the `run()` method on your server instance:

# server.py
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"

if  __name__  == "__main__":
    mcp.run()  # Default: uses STDIO transport

FastMCP supports three transport protocols:

**STDIO (Default)**: Best for local tools and command-line scripts.

mcp.run(transport="stdio")  # Default, so transport argument is optional

**Streamable HTTP**: Recommended for web deployments.

mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")

**SSE**: For compatibility with existing SSE clients.

mcp.run(transport="sse", host="127.0.0.1", port=8000)

See the [**Running Server Documentation**](https://gofastmcp.com/deployment/running-server) for more details.

Contributing
------------

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#contributing)
Contributions are the core of open source! We welcome improvements and features.

### Prerequisites

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#prerequisites)
*   Python 3.10+
*   [uv](https://docs.astral.sh/uv/) (Recommended for environment management)

### Setup

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#setup)
1.   Clone the repository:

git clone https://github.com/jlowin/fastmcp.git 
cd fastmcp 
2.   Create and sync the environment:

uv sync 
This installs all dependencies, including dev tools.

3.   Activate the virtual environment (e.g., `source .venv/bin/activate` or via your IDE).

### Unit Tests

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#unit-tests)
FastMCP has a comprehensive unit test suite. All PRs must introduce or update tests as appropriate and pass the full suite.

Run tests using pytest:

pytest

or if you want an overview of the code coverage

uv run pytest --cov=src --cov=examples --cov-report=html

### Static Checks

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#static-checks)
FastMCP uses `pre-commit` for code formatting, linting, and type-checking. All PRs must pass these checks (they run automatically in CI).

Install the hooks locally:

uv run pre-commit install

The hooks will now run automatically on `git commit`. You can also run them manually at any time:

pre-commit run --all-files
# or via uv
uv run pre-commit run --all-files

### Pull Requests

[](https://github.com/jlowin/fastmcp?tab=readme-ov-file#pull-requests)
1.   Fork the repository on GitHub.
2.   Create a feature branch from `main`.
3.   Make your changes, including tests and documentation updates.
4.   Ensure tests and pre-commit hooks pass.
5.   Commit your changes and push to your fork.
6.   Open a pull request against the `main` branch of `jlowin/fastmcp`.

Please open an issue or discussion for questions or suggestions before starting significant work!
