"""
Phoenix (Arize) observability instrumentation for Brain OS.

OpenTelemetry-based tracing for MCP tools and background tasks.
Provides real-time visibility into tool usage, performance, and errors.
"""

import functools
import logging
import os
from typing import Optional

# Configure Phoenix tracing using arize-phoenix-otel
try:
    from phoenix.otel import register

    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    logging.warning("Phoenix dependencies not installed. Run: uv add arize-phoenix-otel")

logger = logging.getLogger(__name__)

# Global tracer provider (set by register())
_tracer_provider = None

# Phoenix configuration (from environment variables)
PHOENIX_API_KEY = os.getenv("PHOENIX_API_KEY")
PHOENIX_COLLECTOR_ENDPOINT = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
PHOENIX_UI_URL = "https://app.phoenix.arize.com"  # Fixed URL


def setup_phoenix_tracing(
    project_name: str = "brainos",
    endpoint: Optional[str] = None
) -> bool:
    """
    Set up Phoenix tracing for Brain OS using arize-phoenix-otel.

    Automatically picks up configuration from environment variables:
    - PHOENIX_API_KEY: Your Phoenix Cloud API key
    - PHOENIX_COLLECTOR_ENDPOINT: Your Phoenix project endpoint

    Args:
        project_name: Name of the project (default: "brainos")
        endpoint: Phoenix endpoint (default: from PHOENIX_COLLECTOR_ENDPOINT env var)

    Returns:
        True if setup successful, False otherwise

    Example (Phoenix Cloud):
        >>> setup_phoenix_tracing()
        ✅ Phoenix tracing configured: https://app.phoenix.arize.com
        📊 Phoenix UI: https://app.phoenix.arize.com
    """
    global _tracer_provider

    if not PHOENIX_AVAILABLE:
        logger.warning("Phoenix dependencies not available")
        return False

    try:
        # Configure endpoint (from parameter or environment)
        phoenix_endpoint = endpoint or PHOENIX_COLLECTOR_ENDPOINT

        if not phoenix_endpoint:
            logger.warning("PHOENIX_COLLECTOR_ENDPOINT not set, skipping Phoenix setup")
            return False

        # Register with Phoenix using arize-phoenix-otel
        # Environment variables (PHOENIX_API_KEY, PHOENIX_COLLECTOR_ENDPOINT)
        # are automatically picked up by the register() function
        _tracer_provider = register(
            project_name=project_name,
            endpoint=phoenix_endpoint,
            auto_instrument=False  # We'll instrument manually
        )

        logger.info(f"✅ Phoenix tracing configured: {phoenix_endpoint}")
        logger.info(f"📊 Phoenix UI: {PHOENIX_UI_URL}")

        return True

    except Exception as e:
        logger.error(f"Failed to set up Phoenix tracing: {e}")
        return False


def get_tracer(module_name: str):
    """
    Get a tracer for a specific module.

    Args:
        module_name: Name of the module (e.g., "create_memory", "contextual_retrieval")

    Returns:
        Tracer instance

    Example:
        >>> tracer = get_tracer("create_memory")
        >>> with tracer.start_as_current_span("operation") as span:
        >>>     span.set_attribute("key", "value")
    """
    from opentelemetry import trace

    if not PHOENIX_AVAILABLE or _tracer_provider is None:
        # Return no-op tracer if Phoenix not available
        return trace.get_tracer_noop(module_name)

    return trace.get_tracer(module_name)


class BrainOSTracer:
    """
    Convenience class for tracing Brain OS operations.

    Example:
        >>> tracer = BrainOSTracer("create_memory")
        >>> with tracer.trace("create_memory_operation") as span:
        >>>     span.set_attribute("sector", "Semantic")
        >>>     # ... do work ...
        >>>     span.set_attribute("success", True)
    """

    def __init__(self, component: str):
        """
        Initialize tracer for a component.

        Args:
            component: Component name (e.g., "create_memory", "weekly_summary_task")
        """
        self.component = component
        self.tracer = get_tracer(component)

    def trace(self, operation_name: str, **attributes):
        """
        Start a new trace span.

        Args:
            operation_name: Name of the operation
            **attributes: Initial attributes to set on the span

        Returns:
            Context manager for the span

        Example:
            >>> with tracer.trace("get_memory", query="FastAPI") as span:
            >>>     results = await search_memories("FastAPI")
            >>>     span.set_attribute("result_count", len(results))
        """
        span = self.tracer.start_as_current_span(operation_name)

        # Set default attributes
        span.set_attribute("brainos.component", self.component)

        # Set custom attributes
        for key, value in attributes.items():
            span.set_attribute(f"brainos.{key}", value)

        return span


def instrument_mcp_tool(tool_name: str):
    """
    Decorator to automatically instrument MCP tools.

    Args:
        tool_name: Name of the MCP tool

    Example:
        >>> @instrument_mcp_tool("create_memory")
        >>> async def create_memory(content: str, sector: str) -> str:
        >>>     # ... tool logic ...
        >>>     return "Memory stored"
    """
    def decorator(func):
        if not PHOENIX_AVAILABLE:
            return func

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tracer = get_tracer(tool_name)

            with tracer.start_as_current_span(f"mcp_tool:{tool_name}") as span:
                span.set_attribute("mcp.tool", tool_name)

                try:
                    # Extract key parameters
                    if "content" in kwargs:
                        span.set_attribute("params.content_length", len(kwargs["content"]))
                    if "sector" in kwargs:
                        span.set_attribute("params.sector", kwargs["sector"])
                    if "query" in kwargs:
                        span.set_attribute("params.query", kwargs["query"])

                    # Call the function
                    result = await func(*args, **kwargs)

                    span.set_attribute("mcp.success", True)

                    return result

                except Exception as e:
                    span.set_attribute("mcp.success", False)
                    span.set_attribute("mcp.error", str(e))
                    span.record_exception(e)
                    raise

        return wrapper
    return decorator


# =============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON TRACES
# =============================================================================

def trace_llm_call(model: str, prompt: str, response: str, latency_ms: float):
    """
    Trace an LLM call (Groq or OpenRouter).

    Args:
        model: Model name
        prompt: Prompt sent to LLM
        response: Response from LLM
        latency_ms: Latency in milliseconds

    Example:
        >>> trace_llm_call(
        ...     model="llama-3.3-70b",
        ...     prompt="Summarize these memories",
        ...     response="Summary: ...",
        ...     latency_ms=1250
        ... )
    """
    if not PHOENIX_AVAILABLE:
        return

    tracer = get_tracer("llm")

    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("llm.model", model)
        span.set_attribute("llm.prompt_length", len(prompt))
        span.set_attribute("llm.response_length", len(response))
        span.set_attribute("llm.latency_ms", latency_ms)


def trace_neo4j_query(query: str, result_count: int, latency_ms: float):
    """
    Trace a Neo4j query.

    Args:
        query: Cypher query
        result_count: Number of results
        latency_ms: Query latency in milliseconds

    Example:
        >>> trace_neo4j_query(
        ...     query="MATCH (b:Bubble) RETURN b",
        ...     result_count=42,
        ...     latency_ms=45
        ... )
    """
    if not PHOENIX_AVAILABLE:
        return

    tracer = get_tracer("neo4j")

    with tracer.start_as_current_span("neo4j_query") as span:
        span.set_attribute("neo4j.query", query[:100])  # First 100 chars
        span.set_attribute("neo4j.result_count", result_count)
        span.set_attribute("neo4j.latency_ms", latency_ms)


def trace_email_sent(template: str, success: bool, latency_ms: float):
    """
    Trace an email notification.

    Args:
        template: Template name or "custom"
        success: Whether email was sent successfully
        latency_ms: Time to send in milliseconds

    Example:
        >>> trace_email_sent(
        ...     template="weekly_summary",
        ...     success=True,
        ...     latency_ms=850
        ... )
    """
    if not PHOENIX_AVAILABLE:
        return

    tracer = get_tracer("email")

    with tracer.start_as_current_span("email_sent") as span:
        span.set_attribute("email.template", template)
        span.set_attribute("email.success", success)
        span.set_attribute("email.latency_ms", latency_ms)


# =============================================================================
# AUTO-SETUP ON IMPORT
# =============================================================================

if PHOENIX_AVAILABLE:
    setup_phoenix_tracing()
