"""
Summarize Project Flow.
PocketFlow implementation for project summarization (migrated from BaseAgent).

This flow retrieves memories about a project and generates a structured summary.

Configuration-driven: Modify the node config class to change behavior without code changes.
"""

import logging
from dataclasses import dataclass

from pocketflow import AsyncNode, AsyncFlow

from src.utils.llm import get_openrouter_client, get_openrouter_model

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SummarizeProjectConfig:
    """
    Configuration for the summarize project flow.

    Modify these values to change behavior without touching code.
    """

    model_task: str = "creative"
    """OpenRouter model task: creative, researching, or planning"""

    temperature: float = 0.7
    """LLM temperature (0.0 = deterministic, 1.0 = creative)"""

    max_tokens: int = 2000
    """Maximum tokens in the response"""

    system_prompt: str = "You are a helpful assistant that summarizes project information clearly and concisely."
    """System prompt to set context"""


class GenerateSummaryNode(AsyncNode):
    """
    AsyncNode that generates a project summary from memories.

    This is a single-node flow (Cell in the Fractal DNA architecture).
    For more complex workflows, chain multiple nodes with >> operator.
    """

    config: SummarizeProjectConfig = SummarizeProjectConfig()

    async def prep_async(self, shared):
        """
        Prepare inputs from shared store.

        Args:
            shared: Contains 'project_name' and 'memories' keys

        Returns:
            Tuple of (project_name, memories) for exec_async
        """
        project_name = shared.get("project_name", "")
        memories = shared.get("memories", "")
        return project_name, memories

    async def exec_async(self, inputs):
        """
        Execute the core logic: call LLM to generate summary.

        Args:
            inputs: Tuple of (project_name, memories)

        Returns:
            Generated summary as string
        """
        project_name, memories = inputs

        # Build prompt
        prompt = f"""You are a project summary assistant. Review these memories about the project "{project_name}" and provide a structured summary.

Memories:
{memories}

Please provide a summary with these sections:
1. **Overview**: Brief project description
2. **Key Decisions**: Important decisions made
3. **Action Items**: Outstanding tasks
4. **Notes**: Any other relevant information

Format your response in Markdown."""

        # Get OpenRouter client and model
        client = await get_openrouter_client()
        model = get_openrouter_model(self.config.model_task)

        # Call LLM
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content

    async def post_async(self, shared, prep_res, exec_res):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async (project_name, memories)
            exec_res: Result from exec_async (generated summary)

        Returns:
            Action string (always "default" for this single-node flow)
        """
        # Store the summary in shared store
        shared["summary"] = exec_res
        shared["project_name"] = prep_res[0]

        logger.info(f"Generated summary for project: {prep_res[0]}")

        return "default"


# Create the flow (can be chained with other nodes in the future)
summarize_project_flow = AsyncFlow(start=GenerateSummaryNode())


# Convenience function for direct usage
async def summarize_project(project_name: str, memories: str) -> str:
    """
    Generate a project summary using the PocketFlow.

    Args:
        project_name: Name of the project
        memories: Formatted memories string

    Returns:
        Generated summary as string
    """
    shared = {
        "project_name": project_name,
        "memories": memories
    }

    await summarize_project_flow.run_async(shared)

    return shared.get("summary", "")
