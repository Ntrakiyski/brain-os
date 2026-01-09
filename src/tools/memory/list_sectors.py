"""
Memory sector listing tool.
Returns static information about the five-sector ontology.
"""


def register_list_sectors(mcp) -> None:
    """Register the list_sectors tool with FastMCP."""

    @mcp.tool
    async def list_sectors() -> str:
        """
        List all available cognitive sectors in the Brain OS ontology.

        Returns the five-sector ontology with descriptions.
        """
        sectors = {
            "Episodic": "Events and experiences (What happened and when)",
            "Semantic": "Hard facts and knowledge (Requirements, names, technical data)",
            "Procedural": "Habits and workflows (The 'My Way' protocol and brand behaviors)",
            "Emotional": "Sentiment and vibe (Tracking morale, frustration, excitement)",
            "Reflective": "Meta-memory (Logs of how the system synthesizes information)",
        }

        output = ["Brain OS Five-Sector Ontology:\n"]
        for sector, description in sectors.items():
            output.append(f"- {sector}: {description}")

        return "\n".join(output)
