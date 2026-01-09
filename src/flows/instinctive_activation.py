"""
Instinctive Activation Flow.
PocketFlow implementation for automatic memory activation based on context.

This flow implements the "oven analogy" - knowledge that automatically surfaces
without conscious search, like knowing the oven is hot without thinking about it.

Architecture:
1. AnalyzeInputNode: Extract concepts from user input (Groq ~100ms)
2. FindInstinctiveMemoriesNode: Retrieve instinctive bubbles matching concepts (Neo4j)
"""

import logging

from pocketflow import AsyncNode, AsyncFlow

from src.database.queries.memory import search_instinctive_bubbles
from src.utils.llm import get_groq_client

logger = logging.getLogger(__name__)


class AnalyzeInputNode(AsyncNode):
    """
    AsyncNode that quickly analyzes user input for concept triggers.

    Uses Groq (fast ~100ms) for concept extraction.
    This is a "Cell" in the Fractal DNA architecture - atomic operation.
    """

    async def prep_async(self, shared):
        """
        Prepare user input from shared store.

        Args:
            shared: Contains 'user_input' key

        Returns:
            User input string for exec_async
        """
        return shared.get("user_input", "")

    async def exec_async(self, user_input):
        """
        Execute concept extraction using Groq LLM.

        Args:
            user_input: User's message to analyze

        Returns:
            List of concept dictionaries with name and salience
        """
        groq = get_groq_client()
        from src.utils.llm import get_groq_model

        model = get_groq_model()

        prompt = f"""Extract key concepts from this message: "{user_input}"

Return JSON only (no markdown, no code blocks):
{{
    "concepts": [
        {{"name": "concept1", "salience": 0.8}},
        {{"name": "concept2", "salience": 0.6}}
    ]
}}

Rules:
- Extract 2-5 key concepts (people, projects, technologies, topics)
- Assign salience 0.0-1.0 based on importance
- Return valid JSON only
"""

        try:
            response = groq.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            concepts = result.get("concepts", [])

            logger.info(f"Extracted {len(concepts)} concepts from input")
            return concepts

        except Exception as e:
            logger.warning(f"Failed to extract concepts: {e}, using fallback")
            # Fallback: extract simple keywords (split by spaces, filter short words)
            words = user_input.lower().split()
            concepts = []
            for word in set(words):
                if len(word) > 4:  # Only meaningful words
                    concepts.append({"name": word, "salience": 0.5})
            return concepts[:5]  # Limit to 5

    async def post_async(self, shared, prep_res, concepts):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async (user_input)
            exec_res: Result from exec_async (concepts list)

        Returns:
            Action string (always "default" for this flow)
        """
        # Store concepts in shared store
        shared["concepts"] = concepts

        # Calculate max salience for downstream nodes
        max_salience = max([c.get("salience", 0.5) for c in concepts], default=0.5)
        shared["max_concept_salience"] = max_salience

        logger.info(f"Concept analysis complete: {len(concepts)} concepts, max_salience={max_salience}")

        return "default"


class FindInstinctiveMemoriesNode(AsyncNode):
    """
    AsyncNode that finds instinctive memories matching the extracted concepts.

    Queries Neo4j for bubbles with memory_type='instinctive' and
    activation_threshold < concept salience.
    """

    async def prep_async(self, shared):
        """
        Prepare driver and concepts from shared store.

        Args:
            shared: Contains 'neo4j_driver' and 'concepts' keys

        Returns:
            Tuple of (concepts list, max_salience) for exec_async
        """
        concepts = shared.get("concepts", [])
        max_salience = shared.get("max_concept_salience", 0.5)
        return concepts, max_salience

    async def exec_async(self, inputs):
        """
        Execute Neo4j query for instinctive bubbles.

        Args:
            inputs: Tuple of (concepts list, max_salience)

        Returns:
            List of BubbleResponse objects
        """
        concepts, max_salience = inputs

        if not concepts:
            return []

        # Extract concept names
        concept_names = [c["name"] for c in concepts]

        # Query Neo4j for instinctive memories
        # Use max_salience + 0.2 as threshold (concepts with higher salience trigger more memories)
        salience_threshold = min(max_salience + 0.2, 1.0)

        bubbles = await search_instinctive_bubbles(
            concepts=concept_names,
            salience_threshold=salience_threshold,
            limit=10
        )

        logger.info(f"Found {len(bubbles)} instinctive bubbles for {len(concepts)} concepts")

        return bubbles

    async def post_async(self, shared, prep_res, bubbles):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async (concepts, max_salience)
            exec_res: Result from exec_async (bubbles list)

        Returns:
            Action string (always "default" - end of flow)
        """
        # Store results in shared store
        shared["instinctive_memories"] = bubbles

        logger.info(f"Instinctive activation complete: {len(bubbles)} memories activated")

        return "default"


# Wire the flow: analyze -> find_instinctive
analyze = AnalyzeInputNode()
find_instinctive = FindInstinctiveMemoriesNode()

analyze >> find_instinctive
instinctive_activation_flow = AsyncFlow(start=analyze)


# Convenience function for direct usage
async def activate_instinctive_memories(user_input: str) -> list:
    """
    Activate instinctive memories based on user input.

    Args:
        user_input: User's message to analyze

    Returns:
        List of activated BubbleResponse objects
    """
    from src.database.connection import get_driver

    shared = {
        "neo4j_driver": get_driver(),
        "user_input": user_input
    }

    await instinctive_activation_flow.run_async(shared)

    return shared.get("instinctive_memories", [])
