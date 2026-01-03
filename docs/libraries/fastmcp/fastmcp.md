# Installation

## Install FastMCP

We recommend using [uv](https://docs.astral.sh/uv/getting-started/installation/) to install and manage FastMCP.

If you plan to use FastMCP in your project, you can add it as a dependency with:

```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
uv add fastmcp
```

Alternatively, you can install it directly with `pip` or `uv pip`:

<CodeGroup>
  ```bash uv theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
  uv pip install fastmcp
  ```

  ```bash pip theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
  pip install fastmcp
  ```
</CodeGroup>

<Warning>
  **FastMCP 3.0** is in development and may include breaking changes. To avoid unexpected issues, pin your dependency to v2: `fastmcp<3`
</Warning>

### Verify Installation

To verify that FastMCP is installed correctly, you can run the following command:

```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
fastmcp version
```

You should see output like the following:

```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
$ fastmcp version

FastMCP version:                           2.11.3
MCP version:                               1.12.4
Python version:                            3.12.2
Platform:            macOS-15.3.1-arm64-arm-64bit
FastMCP root path:            ~/Developer/fastmcp
```

### Dependency Licensing

<Info>
  FastMCP depends on Cyclopts for CLI functionality. Cyclopts v4 includes docutils as a transitive dependency, which has complex licensing that may trigger compliance reviews in some organizations.

  If this is a concern, you can install Cyclopts v5 alpha which removes this dependency:

  ```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
  pip install "cyclopts>=5.0.0a1"
  ```

  Alternatively, wait for the stable v5 release. See [this issue](https://github.com/BrianPugh/cyclopts/issues/672) for details.
</Info>

## Upgrading from the Official MCP SDK

Upgrading from the official MCP SDK's FastMCP 1.0 to FastMCP 2.0 is generally straightforward. The core server API is highly compatible, and in many cases, changing your import statement from `from mcp.server.fastmcp import FastMCP` to `from fastmcp import FastMCP` will be sufficient.

```python {5} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
# Before
# from mcp.server.fastmcp import FastMCP

# After
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")
```

<Warning>
  Prior to `fastmcp==2.3.0` and `mcp==1.8.0`, the 2.x API always mirrored the official 1.0 API. However, as the projects diverge, this can not be guaranteed. You may see deprecation warnings if you attempt to use 1.0 APIs in FastMCP 2.x. Please refer to this documentation for details on new capabilities.
</Warning>

## Versioning Policy

FastMCP follows semantic versioning with pragmatic adaptations for the rapidly evolving MCP ecosystem. Breaking changes may occur in minor versions (e.g., 2.3.x to 2.4.0) when necessary to stay current with the MCP Protocol.

For production use, always pin to exact versions:

```
fastmcp==2.11.0  # Good
fastmcp>=2.11.0  # Bad - will install breaking changes
```

See the full [versioning and release policy](/development/releases#versioning-policy) for details on our public API, deprecation practices, and breaking change philosophy.

## Contributing to FastMCP

Interested in contributing to FastMCP? See the [Contributing Guide](/development/contributing) for details on:

* Setting up your development environment
* Running tests and pre-commit hooks
* Submitting issues and pull requests
* Code standards and review process


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt
# Quickstart

Welcome! This guide will help you quickly set up FastMCP, run your first MCP server, and deploy a server to FastMCP Cloud.

If you haven't already installed FastMCP, follow the [installation instructions](/getting-started/installation).

## Create a FastMCP Server

A FastMCP server is a collection of tools, resources, and other MCP components. To create a server, start by instantiating the `FastMCP` class.

Create a new file called `my_server.py` and add the following code:

```python my_server.py theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")
```

That's it! You've created a FastMCP server, albeit a very boring one. Let's add a tool to make it more interesting.

## Add a Tool

To add a tool that returns a simple greeting, write a function and decorate it with `@mcp.tool` to register it with the server:

```python my_server.py {5-7} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## Run the Server

The simplest way to run your FastMCP server is to call its `run()` method. You can choose between different transports, like `stdio` for local servers, or `http` for remote access:

<CodeGroup>
  ```python my_server.py (stdio) {9, 10} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
  from fastmcp import FastMCP

  mcp = FastMCP("My MCP Server")

  @mcp.tool
  def greet(name: str) -> str:
      return f"Hello, {name}!"

  if __name__ == "__main__":
      mcp.run()
  ```

  ```python my_server.py (HTTP) {9, 10} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
  from fastmcp import FastMCP

  mcp = FastMCP("My MCP Server")

  @mcp.tool
  def greet(name: str) -> str:
      return f"Hello, {name}!"

  if __name__ == "__main__":
      mcp.run(transport="http", port=8000)
  ```
</CodeGroup>

This lets us run the server with `python my_server.py`. The stdio transport is the traditional way to connect MCP servers to clients, while the HTTP transport enables remote connections.

<Tip>
  Why do we need the `if __name__ == "__main__":` block?

  The `__main__` block is recommended for consistency and compatibility, ensuring your server works with all MCP clients that execute your server file as a script. Users who will exclusively run their server with the FastMCP CLI can omit it, as the CLI imports the server object directly.
</Tip>

### Using the FastMCP CLI

You can also use the `fastmcp run` command to start your server. Note that the FastMCP CLI **does not** execute the `__main__` block of your server file. Instead, it imports your server object and runs it with whatever transport and options you provide.

For example, to run this server with the default stdio transport (no matter how you called `mcp.run()`), you can use the following command:

```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
fastmcp run my_server.py:mcp
```

To run this server with the HTTP transport, you can use the following command:

```bash  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
fastmcp run my_server.py:mcp --transport http --port 8000
```

## Call Your Server

Once your server is running with HTTP transport, you can connect to it with a FastMCP client or any LLM client that supports the MCP protocol:

```python my_client.py theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

asyncio.run(call_tool("Ford"))
```

Note that:

* FastMCP clients are asynchronous, so we need to use `asyncio.run` to run the client
* We must enter a client context (`async with client:`) before using the client
* You can make multiple client calls within the same context

## Deploy to FastMCP Cloud

[FastMCP Cloud](https://fastmcp.cloud) is a hosting service run by the FastMCP team at [Prefect](https://www.prefect.io/fastmcp). It is optimized to deploy authenticated FastMCP servers as quickly as possible, giving you a secure URL that you can plug into any LLM client.

<Info>
  FastMCP Cloud is **free for personal servers** and offers simple pay-as-you-go pricing for teams.
</Info>

To deploy your server, you'll need a [GitHub account](https://github.com). Once you have one, you can deploy your server in three steps:

1. Push your `my_server.py` file to a GitHub repository
2. Sign in to [FastMCP Cloud](https://fastmcp.cloud) with your GitHub account
3. Create a new project from your repository and enter `my_server.py:mcp` as the server entrypoint

That's it! FastMCP Cloud will build and deploy your server, making it available at a URL like `https://your-project.fastmcp.app/mcp`. You can chat with it to test its functionality, or connect to it from any LLM client that supports the MCP protocol.

For more details, see the [FastMCP Cloud guide](/deployment/fastmcp-cloud).


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt