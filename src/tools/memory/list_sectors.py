"""
Memory sector listing tool.
Returns static information about the five-sector ontology.
"""


def register_list_sectors(mcp) -> None:
    """Register the list_sectors tool with FastMCP."""

    @mcp.tool
    async def list_sectors() -> str:
        """
        Understand cognitive state through sector distribution.

        **Use this to check cognitive balance.**

        Returns:
        - Memory count per sector
        - Percentage distribution
        -Formatted table

        Ideal Distribution (Aim for This):
        - Semantic: 25-35% (facts, decisions, knowledge)
        - Procedural: 20-30% (skills, workflows)
        - Episodic: 15-25% (events, experiences)
        - Emotional: 5-15% (feelings, reactions)
        - Reflective: 5-15% (insights, learnings)

        Imbalance Indicators:
        - **Too much Procedural**: You're doing, not thinking
          → Add Reflective memories (process experiences)

        - **Too much Episodic**: You're experiencing, not learning
          → Add Reflective memories (extract insights)

        - **Too much Semantic**: You're planning, not executing
          → Add Procedural memories (document workflows)

        - **Too much Emotional**: You're feeling, not processing
          → Add Reflective memories (make sense of emotions)

        - **Too much Reflective**: You're analyzing, not acting
          → Add Procedural memories (take action)

        The Five Sectors Explained:
        - **Episodic**: Events and experiences ("What happened")
        - **Semantic**: Facts and knowledge ("What is true")
        - **Procedural**: Skills and workflows ("How to do things")
        - **Emotional**: Sentiment and reactions ("How it felt")
        - **Reflective**: Meta-memory ("What I learned")
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
