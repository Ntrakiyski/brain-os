"""
Contextual Retrieval Flow.
PocketFlow implementation for deep memory retrieval with contextual understanding.

This flow implements a 3-agent system:
1. PreQueryContextNode: Analyze context before querying (Groq ~100ms)
2. ContextualQueryNode: Query Neo4j with smart filters
3. PostQuerySynthesizeNode: Synthesize results and find relationships (OpenRouter ~2-5s)

This is an "Organ" in the Fractal DNA architecture - specialized agent cluster.
"""

import logging

from pocketflow import AsyncNode, AsyncFlow

from src.database.connection import get_driver
from src.database.queries.memory import search_bubbles
from src.utils.llm import get_groq_client, get_groq_model, get_openrouter_client, get_openrouter_model

logger = logging.getLogger(__name__)


class PreQueryContextNode(AsyncNode):
    """
    AsyncNode that analyzes context before querying Neo4j.

    Uses Groq (fast ~100ms) for context understanding.
    Expands or narrows search based on conversation context.
    """

    async def prep_async(self, shared):
        """
        Prepare input and context from shared store.

        Args:
            shared: Contains 'user_input' and optional 'conversation_history'

        Returns:
            Tuple of (user_input, conversation_history, time_scope, salience_filter)
        """
        user_input = shared.get("user_input", "")
        conversation_history = shared.get("conversation_history", [])
        time_scope = shared.get("time_scope", "auto")
        salience_filter = shared.get("salience_filter", "auto")

        return user_input, conversation_history, time_scope, salience_filter

    async def exec_async(self, inputs):
        """
        Execute context analysis using Groq LLM.

        Args:
            inputs: Tuple of (user_input, conversation_history, time_scope, salience_filter)

        Returns:
            Context dictionary with intent, concepts, time_scope, salience_filter
        """
        user_input, conversation_history, time_scope, salience_filter = inputs

        # Format conversation history
        history_text = "\n".join([f"- {msg}" for msg in conversation_history[-5:]]) if conversation_history else "None"

        groq = get_groq_client()
        model = get_groq_model()

        prompt = f"""Analyze this conversation context:

User said: "{user_input}"

History:
{history_text}

Extract:
1. Primary intent (what are they looking for?)
2. Related concepts (to expand search)
3. Time scope: "recent" (last 30 days) or "all_time" {"[override: {time_scope}]" if time_scope != "auto" else ""}
4. Salience filter: "high" (>0.6 salience) or "any" {"[override: {salience_filter}]" if salience_filter != "auto" else ""}

Return JSON only (no markdown):
{{
    "intent": "primary_intent",
    "related_concepts": ["concept1", "concept2"],
    "time_scope": "recent or all_time",
    "salience_filter": "high or any"
}}

Rules:
- Extract 2-4 related concepts
- Choose time_scope and salience_filter based on context
- Return valid JSON only
"""

        try:
            response = groq.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            import json
            context = json.loads(response.choices[0].message.content)

            logger.info(f"Context analysis: intent={context.get('intent')}, concepts={len(context.get('related_concepts', []))}")

            return context

        except Exception as e:
            logger.warning(f"Failed to analyze context: {e}, using fallback")
            # Fallback: basic context
            return {
                "intent": "search",
                "related_concepts": [],
                "time_scope": "all_time" if time_scope == "auto" else time_scope,
                "salience_filter": "any" if salience_filter == "auto" else salience_filter
            }

    async def post_async(self, shared, prep_res, context):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async
            exec_res: Result from exec_async (context dictionary)

        Returns:
            Action "query" to proceed to next node
        """
        shared["query_context"] = context

        logger.info(f"Pre-query complete: intent={context.get('intent')}, scope={context.get('time_scope')}")

        return "query"


class ContextualQueryNode(AsyncNode):
    """
    AsyncNode that queries Neo4j with context-aware parameters.

    Builds dynamic Cypher based on pre-query context.
    """

    async def prep_async(self, shared):
        """
        Prepare driver and context from shared store.

        Args:
            shared: Contains 'neo4j_driver' and 'query_context'

        Returns:
            Tuple of (driver, context, user_input)
        """
        driver = shared.get("neo4j_driver")
        context = shared.get("query_context", {})
        user_input = shared.get("user_input", "")

        if not driver:
            driver = await get_driver()

        return driver, context, user_input

    async def exec_async(self, inputs):
        """
        Execute Neo4j query with context-aware filters.

        Args:
            inputs: Tuple of (driver, context, user_input)

        Returns:
            Dictionary with 'bubbles' list and 'relations' list
        """
        from neo4j import AsyncGraphDatabase

        driver, context, user_input = inputs

        # Build base query
        query = """
            MATCH (b:Bubble)
            WHERE b.valid_to IS NULL
        """

        params = {}

        # Add main content filter (include user_input and related concepts)
        search_terms = [user_input]
        search_terms.extend(context.get("related_concepts", []))

        # Build OR conditions for search terms
        or_conditions = " OR ".join([
            f"toLower(b.content) CONTAINS toLower($search{i})"
            for i in range(len(search_terms))
        ])
        query += f" AND ({or_conditions})"

        for i, term in enumerate(search_terms):
            params[f"search{i}"] = term

        # Add time filter
        time_scope = context.get("time_scope", "all_time")
        if time_scope == "recent":
            query += " AND b.created_at > datetime() - duration('P30D')"

        # Add salience filter
        salience_filter = context.get("salience_filter", "any")
        if salience_filter == "high":
            query += " AND b.salience > 0.6"

        query += """
            RETURN b,
                   [(b)-[rel:LINKED]->(other) | {
                       from: id(b),
                       to: id(other),
                       type: rel.type
                   }] as relations
            ORDER BY b.salience DESC
            LIMIT 20
        """

        async with driver.session() as session:
            result = await session.run(query, **params)

            bubbles = []
            all_relations = []

            async for record in result:
                node = record["b"]
                bubbles.append({
                    "id": str(node.element_id),
                    "content": node["content"],
                    "sector": node["sector"],
                    "source": node["source"],
                    "salience": node["salience"],
                    "created_at": node["created_at"],
                    "memory_type": node.get("memory_type", "thinking"),
                    "activation_threshold": node.get("activation_threshold", 0.65),
                })
                all_relations.extend(record.get("relations", []))

        logger.info(f"Contextual query: found {len(bubbles)} bubbles, {len(all_relations)} relations")

        return {"bubbles": bubbles, "relations": all_relations}

    async def post_async(self, shared, prep_res, results):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async
            exec_res: Result from exec_async (bubbles and relations)

        Returns:
            Action "synthesize" to proceed to next node
        """
        shared["query_results"] = results["bubbles"]
        shared["relations"] = results["relations"]

        logger.info(f"Query complete: {len(results['bubbles'])} bubbles retrieved")

        return "synthesize"


class PostQuerySynthesizeNode(AsyncNode):
    """
    AsyncNode that synthesizes and contextualizes query results.

    Uses OpenRouter (deep thinking ~2-5s) for synthesis.
    Groups results by theme, highlights key insights, identifies relationships.
    """

    async def prep_async(self, shared):
        """
        Prepare results and context from shared store.

        Args:
            shared: Contains 'query_results', 'relations', 'query_context'

        Returns:
            Tuple of (bubbles, relations, context)
        """
        bubbles = shared.get("query_results", [])
        relations = shared.get("relations", [])
        context = shared.get("query_context", {})

        return bubbles, relations, context

    async def exec_async(self, inputs):
        """
        Execute synthesis using OpenRouter LLM.

        Args:
            inputs: Tuple of (bubbles, relations, context)

        Returns:
            Synthesis dictionary with themes, highlights, relationships
        """
        bubbles, relations, context = inputs

        if not bubbles:
            return {
                "summary": "No memories found",
                "bubbles": [],
                "themes": [],
                "highlights": [],
                "relationships": []
            }

        # Format bubbles for LLM
        bubble_text = "\n".join([
            f"[{i}] {b['sector']}: {b['content'][:150]}{'...' if len(b['content']) > 150 else ''}"
            for i, b in enumerate(bubbles[:15])
        ])

        # Format relations
        relation_text = "\n".join([
            f"- {r['from']} → {r['to']}: {r['type']}"
            for r in relations[:10]
        ]) if relations else "No relations found"

        client = get_openrouter_client()
        model = get_openrouter_model("researching")

        prompt = f"""Context: User is interested in "{context.get('intent', 'search')}"

Found {len(bubbles)} memories:

{bubble_text}

Relations:
{relation_text}

Synthesize these results:
1. Group by theme (max 3 themes)
2. Identify 2-3 most relevant highlights with explanations
3. List key relationships (max 5)

Return JSON only:
{{
    "themes": [
        {{"name": "theme_name", "relevance": "high|medium|low", "bubble_indices": [0, 1]}}
    ],
    "highlights": [
        {{"content": "summary", "relevance": "why this matters"}}
    ],
    "relationships": [
        {{"from": "memory_summary", "to": "memory_summary", "type": "relation_type"}}
    ]
}}
"""

        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            import json
            synthesis = json.loads(response.choices[0].message.content)
            synthesis["bubbles"] = bubbles

            logger.info(f"Synthesis complete: {len(synthesis.get('themes', []))} themes, {len(synthesis.get('highlights', []))} highlights")

            return synthesis

        except Exception as e:
            logger.warning(f"Failed to synthesize: {e}, using basic format")
            # Fallback: basic structure
            return {
                "bubbles": bubbles,
                "themes": [{"name": "Search Results", "relevance": "medium", "bubble_indices": list(range(len(bubbles)))}],
                "highlights": [{"content": f"Found {len(bubbles)} memories", "relevance": "Search results"}],
                "relationships": []
            }

    async def post_async(self, shared, prep_res, synthesis):
        """
        Post-process and write to shared store.

        Args:
            shared: The shared store dictionary
            prep_res: Result from prep_async
            exec_res: Result from exec_async (synthesis dictionary)

        Returns:
            Action "default" - end of flow
        """
        shared["synthesis"] = synthesis

        logger.info(f"Post-query synthesis complete: {len(synthesis.get('bubbles', []))} bubbles processed")

        return "default"


# Wire the flow: pre_query -> query -> post_query
pre_query = PreQueryContextNode()
query_db = ContextualQueryNode()
post_query = PostQuerySynthesizeNode()

pre_query - "query" >> query_db
query_db - "synthesize" >> post_query

contextual_retrieval_flow = AsyncFlow(start=pre_query)


# Convenience function for direct usage
async def retrieve_with_context(
    user_input: str,
    conversation_history: list[str] = None,
    time_scope: str = "auto",
    salience_filter: str = "auto"
) -> dict:
    """
    Retrieve memories with contextual understanding.

    Args:
        user_input: What the user is looking for
        conversation_history: Recent messages for context
        time_scope: "recent", "all_time", or "auto"
        salience_filter: "high", "any", or "auto"

    Returns:
        Synthesis dictionary with themes, highlights, relationships
    """
    driver = await get_driver()

    shared = {
        "neo4j_driver": driver,
        "user_input": user_input,
        "conversation_history": conversation_history or [],
        "time_scope": time_scope,
        "salience_filter": salience_filter
    }

    await contextual_retrieval_flow.run_async(shared)

    return shared.get("synthesis", {})
