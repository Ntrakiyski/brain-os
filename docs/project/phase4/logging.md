# Client Logging

> Send log messages back to MCP clients through the context.

export const VersionBadge = ({version}) => {
  return <Badge stroke size="lg" icon="gift" iconType="regular" className="version-badge">
            New in version <code>{version}</code>
        </Badge>;
};

<Tip>
  This documentation covers **MCP client logging** - sending messages from your server to MCP clients. For standard server-side logging (e.g., writing to files, console), use `fastmcp.utilities.logging.get_logger()` or Python's built-in `logging` module.
</Tip>

Server logging allows MCP tools to send debug, info, warning, and error messages back to the client. This provides visibility into function execution and helps with debugging during development and operation.

## Why Use Server Logging?

Server logging is essential for:

* **Debugging**: Send detailed execution information to help diagnose issues
* **Progress visibility**: Keep users informed about what the tool is doing
* **Error reporting**: Communicate problems and their context to clients
* **Audit trails**: Create records of tool execution for compliance or analysis

Unlike standard Python logging, MCP server logging sends messages directly to the client, making them visible in the client's interface or logs.

### Basic Usage

Use the context logging methods within any tool function:

```python {8-9, 13, 17, 21} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP, Context

mcp = FastMCP("LoggingDemo")

@mcp.tool
async def analyze_data(data: list[float], ctx: Context) -> dict:
    """Analyze numerical data with comprehensive logging."""
    await ctx.debug("Starting analysis of numerical data")
    await ctx.info(f"Analyzing {len(data)} data points")
    
    try:
        if not data:
            await ctx.warning("Empty data list provided")
            return {"error": "Empty data list"}
        
        result = sum(data) / len(data)
        await ctx.info(f"Analysis complete, average: {result}")
        return {"average": result, "count": len(data)}
        
    except Exception as e:
        await ctx.error(f"Analysis failed: {str(e)}")
        raise
```

## Structured Logging with `extra`

All logging methods (`debug`, `info`, `warning`, `error`, `log`) now accept an `extra` parameter, which is a dictionary of arbitrary data. This allows you to send structured data to the client, which is useful for creating rich, queryable logs.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def process_transaction(transaction_id: str, amount: float, ctx: Context):
    await ctx.info(
        f"Processing transaction {transaction_id}",
        extra={
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": "USD"
        }
    )
    # ... processing logic ...
```

## Server Logs

Client Logging in the form of `ctx.log()` and its convenience methods (`debug`, `info`, `warning`, `error`) are meant for sending messages to the MCP clients. Messages sent to clients are also logged to the server's log at `DEBUG` level. Enable debug logging on the server or enable debug logging on the `fastmcp.server.context.to_client` logger to see these messages in the server's log.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
import logging

from fastmcp.utilities.logging import get_logger

to_client_logger = get_logger(name="fastmcp.server.context.to_client")
to_client_logger.setLevel(level=logging.DEBUG)
```

## Logging Methods

<Card icon="code" title="Context Logging Methods">
  <ResponseField name="ctx.debug" type="async method">
    Send debug-level messages for detailed execution information

    <Expandable title="parameters">
      <ResponseField name="message" type="str">
        The debug message to send to the client
      </ResponseField>

      <ResponseField name="extra" type="dict | None" default="None">
        Optional dictionary for structured logging data
      </ResponseField>
    </Expandable>
  </ResponseField>

  <ResponseField name="ctx.info" type="async method">
    Send informational messages about normal execution

    <Expandable title="parameters">
      <ResponseField name="message" type="str">
        The information message to send to the client
      </ResponseField>

      <ResponseField name="extra" type="dict | None" default="None">
        Optional dictionary for structured logging data
      </ResponseField>
    </Expandable>
  </ResponseField>

  <ResponseField name="ctx.warning" type="async method">
    Send warning messages for potential issues that didn't prevent execution

    <Expandable title="parameters">
      <ResponseField name="message" type="str">
        The warning message to send to the client
      </ResponseField>

      <ResponseField name="extra" type="dict | None" default="None">
        Optional dictionary for structured logging data
      </ResponseField>
    </Expandable>
  </ResponseField>

  <ResponseField name="ctx.error" type="async method">
    Send error messages for problems that occurred during execution

    <Expandable title="parameters">
      <ResponseField name="message" type="str">
        The error message to send to the client
      </ResponseField>

      <ResponseField name="extra" type="dict | None" default="None">
        Optional dictionary for structured logging data
      </ResponseField>
    </Expandable>
  </ResponseField>

  <ResponseField name="ctx.log" type="async method">
    Generic logging method with custom level and logger name

    <Expandable title="parameters">
      <ResponseField name="level" type="Literal['debug', 'info', 'warning', 'error']">
        The log level for the message
      </ResponseField>

      <ResponseField name="message" type="str">
        The message to send to the client
      </ResponseField>

      <ResponseField name="logger_name" type="str | None" default="None">
        Optional custom logger name for categorizing messages
      </ResponseField>

      <ResponseField name="extra" type="dict | None" default="None">
        Optional dictionary for structured logging data
      </ResponseField>
    </Expandable>
  </ResponseField>
</Card>

## Log Levels

### Debug

Use for detailed information that's typically only useful when diagnosing problems:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def process_file(file_path: str, ctx: Context) -> str:
    """Process a file with detailed debug logging."""
    await ctx.debug(f"Starting to process file: {file_path}")
    await ctx.debug("Checking file permissions")
    
    # File processing logic
    await ctx.debug("File processing completed successfully")
    return "File processed"
```

### Info

Use for general information about normal program execution:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def backup_database(ctx: Context) -> str:
    """Backup database with progress information."""
    await ctx.info("Starting database backup")
    await ctx.info("Connecting to database")
    await ctx.info("Backup completed successfully")
    return "Database backed up"
```

### Warning

Use for potentially harmful situations that don't prevent execution:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def validate_config(config: dict, ctx: Context) -> dict:
    """Validate configuration with warnings for deprecated options."""
    if "old_api_key" in config:
        await ctx.warning(
            "Using deprecated 'old_api_key' field. Please use 'api_key' instead",
            extra={"deprecated_field": "old_api_key"}
        )
    
    if config.get("timeout", 30) > 300:
        await ctx.warning(
            "Timeout value is very high (>5 minutes), this may cause issues",
            extra={"timeout_value": config.get("timeout")}
        )
    
    return {"status": "valid", "warnings": "see logs"}
```

### Error

Use for error events that might still allow the application to continue:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def batch_process(items: list[str], ctx: Context) -> dict:
    """Process multiple items, logging errors for failed items."""
    successful = 0
    failed = 0
    
    for item in items:
        try:
            # Process item
            successful += 1
        except Exception as e:
            await ctx.error(
                f"Failed to process item '{item}': {str(e)}",
                extra={"failed_item": item}
            )
            failed += 1
    
    return {"successful": successful, "failed": failed}
```

## Client Handling

Log messages are sent to the client through the MCP protocol. How clients handle these messages depends on their implementation:

* **Development clients**: May display logs in real-time for debugging
* **Production clients**: May store logs for later analysis or display to users
* **Integration clients**: May forward logs to external logging systems

See [Client Logging](/clients/logging) for details on how clients can handle server log messages.


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt

# Progress Reporting

> Update clients on the progress of long-running operations through the MCP context.

export const VersionBadge = ({version}) => {
  return <Badge stroke size="lg" icon="gift" iconType="regular" className="version-badge">
            New in version <code>{version}</code>
        </Badge>;
};

Progress reporting allows MCP tools to notify clients about the progress of long-running operations. This enables clients to display progress indicators and provide better user experience during time-consuming tasks.

## Why Use Progress Reporting?

Progress reporting is valuable for:

* **User experience**: Keep users informed about long-running operations
* **Progress indicators**: Enable clients to show progress bars or percentages
* **Timeout prevention**: Demonstrate that operations are actively progressing
* **Debugging**: Track execution progress for performance analysis

### Basic Usage

Use `ctx.report_progress()` to send progress updates to the client:

```python {14, 21} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP, Context
import asyncio

mcp = FastMCP("ProgressDemo")

@mcp.tool
async def process_items(items: list[str], ctx: Context) -> dict:
    """Process a list of items with progress updates."""
    total = len(items)
    results = []
    
    for i, item in enumerate(items):
        # Report progress as we process each item
        await ctx.report_progress(progress=i, total=total)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        results.append(item.upper())
    
    # Report 100% completion
    await ctx.report_progress(progress=total, total=total)
    
    return {"processed": len(results), "results": results}
```

## Method Signature

<Card icon="code" title="Context Progress Method">
  <ResponseField name="ctx.report_progress" type="async method">
    Report progress to the client for long-running operations

    <Expandable title="Parameters">
      <ResponseField name="progress" type="float">
        Current progress value (e.g., 24, 0.75, 1500)
      </ResponseField>

      <ResponseField name="total" type="float | None" default="None">
        Optional total value (e.g., 100, 1.0, 2000). When provided, clients may interpret this as enabling percentage calculation.
      </ResponseField>
    </Expandable>
  </ResponseField>
</Card>

## Progress Patterns

### Percentage-Based Progress

Report progress as a percentage (0-100):

```python {13-14} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def download_file(url: str, ctx: Context) -> str:
    """Download a file with percentage progress."""
    total_size = 1000  # KB
    downloaded = 0
    
    while downloaded < total_size:
        # Download chunk
        chunk_size = min(50, total_size - downloaded)
        downloaded += chunk_size
        
        # Report percentage progress
        percentage = (downloaded / total_size) * 100
        await ctx.report_progress(progress=percentage, total=100)
        
        await asyncio.sleep(0.1)  # Simulate download time
    
    return f"Downloaded file from {url}"
```

### Absolute Progress

Report progress with absolute values:

```python {10} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def backup_database(ctx: Context) -> str:
    """Backup database tables with absolute progress."""
    tables = ["users", "orders", "products", "inventory", "logs"]
    
    for i, table in enumerate(tables):
        await ctx.info(f"Backing up table: {table}")
        
        # Report absolute progress
        await ctx.report_progress(progress=i + 1, total=len(tables))
        
        # Simulate backup time
        await asyncio.sleep(0.5)
    
    return "Database backup completed"
```

### Indeterminate Progress

Report progress without a known total for operations where the endpoint is unknown:

```python {11} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def scan_directory(directory: str, ctx: Context) -> dict:
    """Scan directory with indeterminate progress."""
    files_found = 0
    
    # Simulate directory scanning
    for i in range(10):  # Unknown number of files
        files_found += 1
        
        # Report progress without total for indeterminate operations
        await ctx.report_progress(progress=files_found)
        
        await asyncio.sleep(0.2)
    
    return {"files_found": files_found, "directory": directory}
```

### Multi-Stage Operations

Break complex operations into stages with progress for each:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def data_migration(source: str, destination: str, ctx: Context) -> str:
    """Migrate data with multi-stage progress reporting."""
    
    # Stage 1: Validation (0-25%)
    await ctx.info("Validating source data")
    for i in range(5):
        await ctx.report_progress(progress=i * 5, total=100)
        await asyncio.sleep(0.1)
    
    # Stage 2: Export (25-60%)
    await ctx.info("Exporting data from source")
    for i in range(7):
        progress = 25 + (i * 5)
        await ctx.report_progress(progress=progress, total=100)
        await asyncio.sleep(0.1)
    
    # Stage 3: Transform (60-80%)
    await ctx.info("Transforming data format")
    for i in range(4):
        progress = 60 + (i * 5)
        await ctx.report_progress(progress=progress, total=100)
        await asyncio.sleep(0.1)
    
    # Stage 4: Import (80-100%)
    await ctx.info("Importing to destination")
    for i in range(4):
        progress = 80 + (i * 5)
        await ctx.report_progress(progress=progress, total=100)
        await asyncio.sleep(0.1)
    
    # Final completion
    await ctx.report_progress(progress=100, total=100)
    
    return f"Migration from {source} to {destination} completed"
```

## Client Requirements

Progress reporting requires clients to support progress handling:

* Clients must send a `progressToken` in the initial request to receive progress updates
* If no progress token is provided, progress calls will have no effect (they won't error)
* See [Client Progress](/clients/progress) for details on implementing client-side progress handling


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt
# Storage Backends

> Configure persistent and distributed storage for caching and OAuth state management

export const VersionBadge = ({version}) => {
  return <Badge stroke size="lg" icon="gift" iconType="regular" className="version-badge">
            New in version <code>{version}</code>
        </Badge>;
};

<VersionBadge version="2.13.0" />

FastMCP uses pluggable storage backends for caching responses and managing OAuth state. By default, all storage is in-memory, which is perfect for development but doesn't persist across restarts. FastMCP includes support for multiple storage backends, and you can easily extend it with custom implementations.

<Tip>
  The storage layer is powered by **[py-key-value-aio](https://github.com/strawgate/py-key-value)**, an async key-value library maintained by a core FastMCP maintainer. This library provides a unified interface for multiple backends, making it easy to swap implementations based on your deployment needs.
</Tip>

## Available Backends

### In-Memory Storage

**Best for:** Development, testing, single-process deployments

In-memory storage is the default for all FastMCP storage needs. It's fast, requires no setup, and is perfect for getting started.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from key_value.aio.stores.memory import MemoryStore

# Used by default - no configuration needed
# But you can also be explicit:
cache_store = MemoryStore()
```

**Characteristics:**

* ✅ No setup required
* ✅ Very fast
* ❌ Data lost on restart
* ❌ Not suitable for multi-process deployments

### Disk Storage

**Best for:** Single-server production deployments, persistent caching

Disk storage persists data to the filesystem, allowing it to survive server restarts.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from key_value.aio.stores.disk import DiskStore
from fastmcp.server.middleware.caching import ResponseCachingMiddleware

# Persistent response cache
middleware = ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="/var/cache/fastmcp")
)
```

Or with OAuth token storage:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp.server.auth.providers.github import GitHubProvider
from key_value.aio.stores.disk import DiskStore

auth = GitHubProvider(
    client_id="your-id",
    client_secret="your-secret",
    base_url="https://your-server.com",
    client_storage=DiskStore(directory="/var/lib/fastmcp/oauth")
)
```

**Characteristics:**

* ✅ Data persists across restarts
* ✅ Good performance for moderate load
* ❌ Not suitable for distributed deployments
* ❌ Filesystem access required

### Redis

**Best for:** Distributed production deployments, shared caching across multiple servers

<Note>
  Redis support requires an optional dependency: `pip install 'py-key-value-aio[redis]'`
</Note>

Redis provides distributed caching and state management, ideal for production deployments with multiple server instances.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from key_value.aio.stores.redis import RedisStore
from fastmcp.server.middleware.caching import ResponseCachingMiddleware

# Distributed response cache
middleware = ResponseCachingMiddleware(
    cache_storage=RedisStore(host="redis.example.com", port=6379)
)
```

With authentication:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from key_value.aio.stores.redis import RedisStore

cache_store = RedisStore(
    host="redis.example.com",
    port=6379,
    password="your-redis-password"
)
```

For OAuth token storage:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
import os
from fastmcp.server.auth.providers.github import GitHubProvider
from key_value.aio.stores.redis import RedisStore

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    base_url="https://your-server.com",
    jwt_signing_key=os.environ["JWT_SIGNING_KEY"],
    client_storage=RedisStore(host="redis.example.com", port=6379)
)
```

**Characteristics:**

* ✅ Distributed and highly available
* ✅ Fast in-memory performance
* ✅ Works across multiple server instances
* ✅ Built-in TTL support
* ❌ Requires Redis infrastructure
* ❌ Network latency vs local storage

### Other Backends from py-key-value-aio

The py-key-value-aio library includes additional implementations for various storage systems:

* **DynamoDB** - AWS distributed database
* **MongoDB** - NoSQL document store
* **Elasticsearch** - Distributed search and analytics
* **Memcached** - Distributed memory caching
* **RocksDB** - Embedded high-performance key-value store
* **Valkey** - Redis-compatible server

For configuration details on these backends, consult the [py-key-value-aio documentation](https://github.com/strawgate/py-key-value).

<Warning>
  Before using these backends in production, review the [py-key-value documentation](https://github.com/strawgate/py-key-value) to understand the maturity level and limitations of your chosen backend. Some backends may be in preview or have specific constraints that make them unsuitable for production use.
</Warning>

## Use Cases in FastMCP

### Server-Side OAuth Token Storage

The [OAuth Proxy](/servers/auth/oauth-proxy) and OAuth auth providers use storage for persisting OAuth client registrations and upstream tokens. **By default, storage is automatically encrypted using `FernetEncryptionWrapper`.** When providing custom storage, wrap it in `FernetEncryptionWrapper` to encrypt sensitive OAuth tokens at rest.

**Development (default behavior):**

By default, FastMCP automatically manages keys and storage based on your platform:

* **Mac/Windows**: Keys are auto-managed via system keyring, storage defaults to disk. Suitable **only** for development and local testing.
* **Linux**: Keys are ephemeral, storage defaults to memory.

No configuration needed:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp.server.auth.providers.github import GitHubProvider

auth = GitHubProvider(
    client_id="your-id",
    client_secret="your-secret",
    base_url="https://your-server.com"
)
```

**Production:**

For production deployments, configure explicit keys and persistent network-accessible storage with encryption:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
import os
from fastmcp.server.auth.providers.github import GitHubProvider
from key_value.aio.stores.redis import RedisStore
from key_value.aio.wrappers.encryption import FernetEncryptionWrapper
from cryptography.fernet import Fernet

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    base_url="https://your-server.com",
    # Explicit JWT signing key (required for production)
    jwt_signing_key=os.environ["JWT_SIGNING_KEY"],
    # Encrypted persistent storage (required for production)
    client_storage=FernetEncryptionWrapper(
        key_value=RedisStore(host="redis.example.com", port=6379),
        fernet=Fernet(os.environ["STORAGE_ENCRYPTION_KEY"])
    )
)
```

Both parameters are required for production. **Wrap your storage in `FernetEncryptionWrapper` to encrypt sensitive OAuth tokens at rest** - without it, tokens are stored in plaintext. See [OAuth Token Security](/deployment/http#oauth-token-security) and [Key and Storage Management](/servers/auth/oauth-proxy#key-and-storage-management) for complete setup details.

### Response Caching Middleware

The [Response Caching Middleware](/servers/middleware#caching-middleware) caches tool calls, resource reads, and prompt requests. Storage configuration is passed via the `cache_storage` parameter:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from key_value.aio.stores.disk import DiskStore

mcp = FastMCP("My Server")

# Cache to disk instead of memory
mcp.add_middleware(ResponseCachingMiddleware(
    cache_storage=DiskStore(directory="cache")
))
```

For multi-server deployments sharing a Redis instance:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from key_value.aio.stores.redis import RedisStore
from key_value.aio.wrappers.prefix_collections import PrefixCollectionsWrapper

base_store = RedisStore(host="redis.example.com")
namespaced_store = PrefixCollectionsWrapper(
    key_value=base_store,
    prefix="my-server"
)

middleware = ResponseCachingMiddleware(cache_storage=namespaced_store)
```

### Client-Side OAuth Token Storage

The [FastMCP Client](/clients/client) uses storage for persisting OAuth tokens locally. By default, tokens are stored in memory:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp.client.auth import OAuthClientProvider
from key_value.aio.stores.disk import DiskStore

# Store tokens on disk for persistence across restarts
token_storage = DiskStore(directory="~/.local/share/fastmcp/tokens")

oauth_provider = OAuthClientProvider(
    mcp_url="https://your-mcp-server.com/mcp/sse",
    token_storage=token_storage
)
```

This allows clients to reconnect without re-authenticating after restarts.

## Choosing a Backend

| Backend  | Development | Single Server | Multi-Server | Cloud Native |
| -------- | ----------- | ------------- | ------------ | ------------ |
| Memory   | ✅ Best      | ⚠️ Limited    | ❌            | ❌            |
| Disk     | ✅ Good      | ✅ Recommended | ❌            | ⚠️           |
| Redis    | ⚠️ Overkill | ✅ Good        | ✅ Best       | ✅ Best       |
| DynamoDB | ❌           | ⚠️            | ✅            | ✅ Best (AWS) |
| MongoDB  | ❌           | ⚠️            | ✅            | ✅ Good       |

**Decision tree:**

1. **Just starting?** Use **Memory** (default) - no configuration needed
2. **Single server, needs persistence?** Use **Disk**
3. **Multiple servers or cloud deployment?** Use **Redis** or **DynamoDB**
4. **Existing infrastructure?** Look for a matching py-key-value-aio backend

## More Resources

* [py-key-value-aio GitHub](https://github.com/strawgate/py-key-value) - Full library documentation
* [Response Caching Middleware](/servers/middleware#caching-middleware) - Using storage for caching
* [OAuth Token Security](/deployment/http#oauth-token-security) - Production OAuth configuration
* [HTTP Deployment](/deployment/http) - Complete deployment guide


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt
# MCP Context

> Access MCP capabilities like logging, progress, and resources within your MCP objects.

export const VersionBadge = ({version}) => {
  return <Badge stroke size="lg" icon="gift" iconType="regular" className="version-badge">
            New in version <code>{version}</code>
        </Badge>;
};

When defining FastMCP [tools](/servers/tools), [resources](/servers/resources), resource templates, or [prompts](/servers/prompts), your functions might need to interact with the underlying MCP session or access advanced server capabilities. FastMCP provides the `Context` object for this purpose.

<Note>
  FastMCP uses [Docket](https://github.com/chrisguidry/docket)'s dependency injection system for managing runtime dependencies. This page covers Context and the built-in dependencies; see [Custom Dependencies](#custom-dependencies) for creating your own.
</Note>

## What Is Context?

The `Context` object provides a clean interface to access MCP features within your functions, including:

* **Logging**: Send debug, info, warning, and error messages back to the client
* **Progress Reporting**: Update the client on the progress of long-running operations
* **Resource Access**: List and read data from resources registered with the server
* **Prompt Access**: List and retrieve prompts registered with the server
* **LLM Sampling**: Request the client's LLM to generate text based on provided messages
* **User Elicitation**: Request structured input from users during tool execution
* **State Management**: Store and share data between middleware and the handler within a single request
* **Request Information**: Access metadata about the current request
* **Server Access**: When needed, access the underlying FastMCP server instance

## Accessing the Context

<VersionBadge version="2.14" />

The preferred way to access context is using the `CurrentContext()` dependency:

```python {1, 6} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

mcp = FastMCP(name="Context Demo")

@mcp.tool
async def process_file(file_uri: str, ctx: Context = CurrentContext()) -> str:
    """Processes a file, using context for logging and resource access."""
    await ctx.info(f"Processing {file_uri}")
    return "Processed file"
```

This works with tools, resources, and prompts:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

mcp = FastMCP(name="Context Demo")

@mcp.resource("resource://user-data")
async def get_user_data(ctx: Context = CurrentContext()) -> dict:
    await ctx.debug("Fetching user data")
    return {"user_id": "example"}

@mcp.prompt
async def data_analysis_request(dataset: str, ctx: Context = CurrentContext()) -> str:
    return f"Please analyze the following dataset: {dataset}"
```

**Key Points:**

* Dependency parameters are automatically excluded from the MCP schema—clients never see them.
* Context methods are async, so your function usually needs to be async as well.
* **Each MCP request receives a new context object.** Context is scoped to a single request; state or data set in one request will not be available in subsequent requests.
* Context is only available during a request; attempting to use context methods outside a request will raise errors.

### Legacy Type-Hint Injection

For backwards compatibility, you can still access context by simply adding a parameter with the `Context` type hint. FastMCP will automatically inject the context instance:

```python {1, 6} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP, Context

mcp = FastMCP(name="Context Demo")

@mcp.tool
async def process_file(file_uri: str, ctx: Context) -> str:
    """Processes a file, using context for logging and resource access."""
    # Context is injected automatically based on the type hint
    return "Processed file"
```

This approach still works for tools, resources, and prompts. The parameter name doesn't matter—only the `Context` type hint is important. The type hint can also be a union (`Context | None`) or use `Annotated[]`.

### Via `get_context()` Function

<VersionBadge version="2.2.11" />

For code nested deeper within your function calls where passing context through parameters is inconvenient, use `get_context()` to retrieve the active context from anywhere within a request's execution flow:

```python {2,9} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

mcp = FastMCP(name="Dependency Demo")

# Utility function that needs context but doesn't receive it as a parameter
async def process_data(data: list[float]) -> dict:
    # Get the active context - only works when called within a request
    ctx = get_context()
    await ctx.info(f"Processing {len(data)} data points")

@mcp.tool
async def analyze_dataset(dataset_name: str) -> dict:
    # Call utility function that uses context internally
    data = load_data(dataset_name)
    await process_data(data)
```

**Important Notes:**

* The `get_context()` function should only be used within the context of a server request. Calling it outside of a request will raise a `RuntimeError`.
* The `get_context()` function is server-only and should not be used in client code.

## Context Capabilities

FastMCP provides several advanced capabilities through the context object. Each capability has dedicated documentation with comprehensive examples and best practices:

### Logging

Send debug, info, warning, and error messages back to the MCP client for visibility into function execution.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
await ctx.debug("Starting analysis")
await ctx.info(f"Processing {len(data)} items") 
await ctx.warning("Deprecated parameter used")
await ctx.error("Processing failed")
```

See [Server Logging](/servers/logging) for complete documentation and examples.

### Client Elicitation

<VersionBadge version="2.10.0" />

Request structured input from clients during tool execution, enabling interactive workflows and progressive disclosure. This is a new feature in the 6/18/2025 MCP spec.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
result = await ctx.elicit("Enter your name:", response_type=str)
if result.action == "accept":
    name = result.data
```

See [User Elicitation](/servers/elicitation) for detailed examples and supported response types.

### LLM Sampling

<VersionBadge version="2.0.0" />

Request the client's LLM to generate text based on provided messages, useful for leveraging AI capabilities within your tools.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
response = await ctx.sample("Analyze this data", temperature=0.7)
```

See [LLM Sampling](/servers/sampling) for comprehensive usage and advanced techniques.

### Progress Reporting

Update clients on the progress of long-running operations, enabling progress indicators and better user experience.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
await ctx.report_progress(progress=50, total=100)  # 50% complete
```

See [Progress Reporting](/servers/progress) for detailed patterns and examples.

### Resource Access

List and read data from resources registered with your FastMCP server, allowing access to files, configuration, or dynamic content.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
# List available resources
resources = await ctx.list_resources()

# Read a specific resource
content_list = await ctx.read_resource("resource://config")
content = content_list[0].content
```

**Method signatures:**

* **`ctx.list_resources() -> list[MCPResource]`**: <VersionBadge version="2.13.0" /> Returns list of all available resources
* **`ctx.read_resource(uri: str | AnyUrl) -> list[ReadResourceContents]`**: Returns a list of resource content parts

### Prompt Access

<VersionBadge version="2.13.0" />

List and retrieve prompts registered with your FastMCP server, allowing tools and middleware to discover and use available prompts programmatically.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
# List available prompts
prompts = await ctx.list_prompts()

# Get a specific prompt with arguments
result = await ctx.get_prompt("analyze_data", {"dataset": "users"})
messages = result.messages
```

**Method signatures:**

* **`ctx.list_prompts() -> list[MCPPrompt]`**: Returns list of all available prompts
* **`ctx.get_prompt(name: str, arguments: dict[str, Any] | None = None) -> GetPromptResult`**: Get a specific prompt with optional arguments

### State Management

<VersionBadge version="2.11.0" />

Store and share data between middleware and handlers within a single MCP request. Each MCP request (such as calling a tool, reading a resource, listing tools, or listing resources) receives its own context object with isolated state. Context state is particularly useful for passing information from [middleware](/servers/middleware) to your handlers.

To store a value in the context state, use `ctx.set_state(key, value)`. To retrieve a value, use `ctx.get_state(key)`.

<Warning>
  Context state is scoped to a single MCP request. Each operation (tool call, resource read, list operation, etc.) receives a new context object. State set during one request will not be available in subsequent requests. For persistent data storage across requests, use external storage mechanisms like databases, files, or in-memory caches.
</Warning>

This simplified example shows how to use MCP middleware to store user info in the context state, and how to access that state in a tool:

```python {7-8, 16-17} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp.server.middleware import Middleware, MiddlewareContext

class UserAuthMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):

        # Middleware stores user info in context state
        context.fastmcp_context.set_state("user_id", "user_123")
        context.fastmcp_context.set_state("permissions", ["read", "write"])

        return await call_next(context)

@mcp.tool
async def secure_operation(data: str, ctx: Context) -> str:
    """Tool can access state set by middleware."""

    user_id = ctx.get_state("user_id")  # "user_123"
    permissions = ctx.get_state("permissions")  # ["read", "write"]
    
    if "write" not in permissions:
        return "Access denied"
    
    return f"Processing {data} for user {user_id}"
```

**Method signatures:**

* **`ctx.set_state(key: str, value: Any) -> None`**: Store a value in the context state
* **`ctx.get_state(key: str) -> Any`**: Retrieve a value from the context state (returns None if not found)

**State Inheritance:**
When a new context is created (nested contexts), it inherits a copy of its parent's state. This ensures that:

* State set on a child context never affects the parent context
* State set on a parent context after the child context is initialized is not propagated to the child context

This makes state management predictable and prevents unexpected side effects between nested operations.

### Change Notifications

<VersionBadge version="2.9.1" />

FastMCP automatically sends list change notifications when components (such as tools, resources, or prompts) are added, removed, enabled, or disabled. In rare cases where you need to manually trigger these notifications, you can use the context methods:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def custom_tool_management(ctx: Context) -> str:
    """Example of manual notification after custom tool changes."""
    # After making custom changes to tools
    await ctx.send_tool_list_changed()
    await ctx.send_resource_list_changed()
    await ctx.send_prompt_list_changed()
    return "Notifications sent"
```

These methods are primarily used internally by FastMCP's automatic notification system and most users will not need to invoke them directly.

### FastMCP Server

To access the underlying FastMCP server instance, you can use the `ctx.fastmcp` property:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def my_tool(ctx: Context) -> None:
    # Access the FastMCP server instance
    server_name = ctx.fastmcp.name
    ...
```

### MCP Request

Access metadata about the current request and client.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
async def request_info(ctx: Context) -> dict:
    """Return information about the current request."""
    return {
        "request_id": ctx.request_id,
        "client_id": ctx.client_id or "Unknown client"
    }
```

**Available Properties:**

* **`ctx.request_id -> str`**: Get the unique ID for the current MCP request
* **`ctx.client_id -> str | None`**: Get the ID of the client making the request, if provided during initialization
* **`ctx.session_id -> str | None`**: Get the MCP session ID for session-based data sharing (HTTP transports only)

#### Request Context Availability

<VersionBadge version="2.13.1" />

The `ctx.request_context` property provides access to the underlying MCP request context, but returns `None` when the MCP session has not been established yet. This typically occurs:

* During middleware execution in the `on_request` hook before the MCP handshake completes
* During the initialization phase of client connections

The MCP request context is distinct from the HTTP request. For HTTP transports, HTTP request data may be available even when the MCP session is not yet established.

To safely access the request context in situations where it may not be available:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_request

mcp = FastMCP(name="Session Aware Demo")

@mcp.tool
async def session_info(ctx: Context) -> dict:
    """Return session information when available."""

    # Check if MCP session is available
    if ctx.request_context:
        # MCP session available - can access MCP-specific attributes
        return {
            "session_id": ctx.session_id,
            "request_id": ctx.request_id,
            "has_meta": ctx.request_context.meta is not None
        }
    else:
        # MCP session not available - use HTTP helpers for request data (if using HTTP transport)
        request = get_http_request()
        return {
            "message": "MCP session not available",
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
```

For HTTP request access that works regardless of MCP session availability (when using HTTP transports), use the [HTTP request helpers](#http-requests) like `get_http_request()` and `get_http_headers()`.

#### Client Metadata

<VersionBadge version="2.13.1" />

Clients can send contextual information with their requests using the `meta` parameter. This metadata is accessible through `ctx.request_context.meta` and is available for all MCP operations (tools, resources, prompts).

The `meta` field is `None` when clients don't provide metadata. When provided, metadata is accessible via attribute access (e.g., `meta.user_id`) rather than dictionary access. The structure of metadata is determined by the client making the request.

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
@mcp.tool
def send_email(to: str, subject: str, body: str, ctx: Context) -> str:
    """Send an email, logging metadata about the request."""

    # Access client-provided metadata
    meta = ctx.request_context.meta

    if meta:
        # Meta is accessed as an object with attribute access
        user_id = meta.user_id if hasattr(meta, 'user_id') else None
        trace_id = meta.trace_id if hasattr(meta, 'trace_id') else None

        # Use metadata for logging, observability, etc.
        if trace_id:
            log_with_trace(f"Sending email for user {user_id}", trace_id)

    # Send the email...
    return f"Email sent to {to}"
```

<Warning>
  The MCP request is part of the low-level MCP SDK and intended for advanced use cases. Most users will not need to use it directly.
</Warning>

## Runtime Dependencies

### HTTP Requests

<VersionBadge version="2.2.11" />

The recommended way to access the current HTTP request is through the `get_http_request()` dependency function:

```python {2, 3, 11} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

mcp = FastMCP(name="HTTP Request Demo")

@mcp.tool
async def user_agent_info() -> dict:
    """Return information about the user agent."""
    # Get the HTTP request
    request: Request = get_http_request()
    
    # Access request data
    user_agent = request.headers.get("user-agent", "Unknown")
    client_ip = request.client.host if request.client else "Unknown"
    
    return {
        "user_agent": user_agent,
        "client_ip": client_ip,
        "path": request.url.path,
    }
```

This approach works anywhere within a request's execution flow, not just within your MCP function. It's useful when:

1. You need access to HTTP information in helper functions
2. You're calling nested functions that need HTTP request data
3. You're working with middleware or other request processing code

### HTTP Headers

<VersionBadge version="2.2.11" />

If you only need request headers and want to avoid potential errors, you can use the `get_http_headers()` helper:

```python {2, 10} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

mcp = FastMCP(name="Headers Demo")

@mcp.tool
async def safe_header_info() -> dict:
    """Safely get header information without raising errors."""
    # Get headers (returns empty dict if no request context)
    headers = get_http_headers()
    
    # Get authorization header
    auth_header = headers.get("authorization", "")
    is_bearer = auth_header.startswith("Bearer ")
    
    return {
        "user_agent": headers.get("user-agent", "Unknown"),
        "content_type": headers.get("content-type", "Unknown"),
        "has_auth": bool(auth_header),
        "auth_type": "Bearer" if is_bearer else "Other" if auth_header else "None",
        "headers_count": len(headers)
    }
```

By default, `get_http_headers()` excludes problematic headers like `host` and `content-length`. To include all headers, use `get_http_headers(include_all=True)`.

### Access Tokens

<VersionBadge version="2.11.0" />

When using authentication with your FastMCP server, you can access the authenticated user's access token information using the `get_access_token()` dependency function:

```python {2, 10} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token, AccessToken

mcp = FastMCP(name="Auth Token Demo")

@mcp.tool
async def get_user_info() -> dict:
    """Get information about the authenticated user."""
    # Get the access token (None if not authenticated)
    token: AccessToken | None = get_access_token()
    
    if token is None:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "client_id": token.client_id,
        "scopes": token.scopes,
        "expires_at": token.expires_at,
        "token_claims": token.claims,  # JWT claims or custom token data
    }
```

This is particularly useful when you need to:

1. **Access user identification** - Get the `client_id` or subject from token claims
2. **Check permissions** - Verify scopes or custom claims before performing operations
3. **Multi-tenant applications** - Extract tenant information from token claims
4. **Audit logging** - Track which user performed which actions

#### Working with Token Claims

The `claims` field contains all the data from the original token (JWT claims for JWT tokens, or custom data for other token types):

```python {2, 3, 9, 12, 15} theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

mcp = FastMCP(name="Multi-tenant Demo")

@mcp.tool
async def get_tenant_data(resource_id: str) -> dict:
    """Get tenant-specific data using token claims."""
    token: AccessToken | None = get_access_token()
    
    # Extract tenant ID from token claims
    tenant_id = token.claims.get("tenant_id") if token else None
    
    # Extract user ID from standard JWT subject claim
    user_id = token.claims.get("sub") if token else None
    
    # Use tenant and user info to authorize and filter data
    if not tenant_id:
        raise ValueError("No tenant information in token")
    
    return {
        "resource_id": resource_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "data": f"Tenant-specific data for {tenant_id}",
    }
```

## Custom Dependencies

<VersionBadge version="2.14" />

FastMCP's dependency injection is powered by [Docket](https://github.com/chrisguidry/docket), which provides a flexible system for injecting values into your functions. Beyond the built-in dependencies like `CurrentContext()`, you can create your own.

### Using `Depends()`

The simplest way to create a custom dependency is with `Depends()`. Pass any callable (sync or async function, or async context manager) and its return value will be injected:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

mcp = FastMCP(name="Custom Deps Demo")

# Simple function dependency
def get_config() -> dict:
    return {"api_url": "https://api.example.com", "timeout": 30}

# Async function dependency
async def get_user_id() -> int:
    return 42

@mcp.tool
async def fetch_data(
    query: str,
    config: dict = Depends(get_config),
    user_id: int = Depends(get_user_id),
) -> str:
    return f"User {user_id} fetching '{query}' from {config['api_url']}"
```

Dependencies using `Depends()` are automatically excluded from the MCP schema—clients never see them as parameters.

### Resource Management with Context Managers

For dependencies that need cleanup (database connections, file handles, etc.), use an async context manager:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

mcp = FastMCP(name="Resource Demo")

@asynccontextmanager
async def get_database():
    db = await connect_to_database()
    try:
        yield db
    finally:
        await db.close()

@mcp.tool
async def query_users(sql: str, db = Depends(get_database)) -> list:
    return await db.execute(sql)
```

The context manager's cleanup code runs after your function completes, even if an error occurs.

### Nested Dependencies

Dependencies can depend on other dependencies:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP
from fastmcp.dependencies import Depends

mcp = FastMCP(name="Nested Demo")

def get_base_url() -> str:
    return "https://api.example.com"

def get_api_client(base_url: str = Depends(get_base_url)) -> dict:
    return {"base_url": base_url, "version": "v1"}

@mcp.tool
async def call_api(endpoint: str, client: dict = Depends(get_api_client)) -> str:
    return f"Calling {client['base_url']}/{client['version']}/{endpoint}"
```

### Advanced: Subclassing `Dependency`

For more complex dependency patterns—like dependencies that need access to Docket's execution context or require custom lifecycle management—you can subclass Docket's `Dependency` class. See the [Docket documentation on dependencies](https://chrisguidry.github.io/docket/dependencies/) for details.


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt