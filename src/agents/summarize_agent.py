"""
Summarize Agent.
Retrieves memories about a project and generates a structured summary.
"""

from src.agents.base import BaseAgent, AgentConfig, OutputFormat


class SummarizeAgent(BaseAgent):
    """
    Agent that summarizes project-related memories.

    Configuration can be modified without changing code:
    - Change the model (provider/task)
    - Adjust the prompt template
    - Modify output format
    - Set temperature and token limits
    """

    config = AgentConfig(
        name="summarize_project",
        model="openrouter/creative",
        prompt_template="""You are a project summary assistant. Review these memories about the project "{project}" and provide a structured summary.

Memories:
{memories}

Please provide a summary with these sections:
1. **Overview**: Brief project description
2. **Key Decisions**: Important decisions made
3. **Action Items**: Outstanding tasks
4. **Notes**: Any other relevant information

Format your response in Markdown.""",
        output_format=OutputFormat.MARKDOWN,
        temperature=0.7,
        max_tokens=2000,
        system_prompt="You are a helpful assistant that summarizes project information clearly and concisely.",
    )
