"""
Query Memories Flow.
Phase 6: AI-powered Q&A with reasoning and confidence scores.

A 4-node PocketFlow implementation that provides direct answers to natural
language questions about your memories, with full reasoning trace and confidence.

Key Features:
- Query classification (factual, rationale, summary, opinion, temporal)
- Hybrid retrieval (keyword + semantic matching)
- Optional reflection for complex queries
- Answer synthesis with memory references [1], [2]
- Confidence scoring (0.0-1.0)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pocketflow import AsyncNode, AsyncFlow

from src.database.connection import get_driver
from src.database.queries.memory import search_bubbles
from src.utils.llm import get_groq_client, get_openrouter_client, get_openrouter_model

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueryAnalysisConfig:
    """Configuration for query analysis node."""

    model_temperature: float = 0.0
    """LLM temperature (0.0 = deterministic for classification)"""

    max_concepts: int = 5
    """Maximum number of key concepts to extract"""

    hedge_words: tuple = (
        "maybe", "perhaps", "possibly", "might", "could be",
        "seems like", "appears to be", "I think", "probably"
    )
    """Words that indicate uncertainty"""


@dataclass(frozen=True)
class HybridRetrievalConfig:
    """Configuration for hybrid retrieval node."""

    keyword_limit: int = 20
    """Maximum results from keyword search"""

    semantic_limit: int = 10
    """Maximum results from semantic search"""

    salience_threshold: float = 0.3
    """Minimum salience score to include"""


@dataclass(frozen=True)
class ReflectionConfig:
    """Configuration for reflection node."""

    enabled: bool = True
    """Whether reflection is enabled"""

    min_results_trigger: int = 3
    """Trigger reflection if fewer than this many results"""

    model_task: str = "researching"
    """OpenRouter model task for reflection"""


@dataclass(frozen=True)
class AnswerSynthesisConfig:
    """Configuration for answer synthesis node."""

    model_task: str = "creative"
    """OpenRouter model task: creative, researching, thinking, or planning"""

    temperature: float = 0.7
    """LLM temperature for synthesis"""

    max_tokens: int = 1500
    """Maximum tokens in the response"""

    min_confidence: float = 0.3
    """Minimum confidence score to return"""

    max_answer_sentences: int = 4
    """Maximum sentences in the direct answer"""


class QueryAnalysisNode(AsyncNode):
    """
    Analyze the user's query to determine retrieval strategy.

    Uses Groq for fast classification (~100ms).

    Extracts:
    - Query type (factual, rationale, summary, opinion, temporal)
    - Key concepts for retrieval
    - Hedge words (indicates uncertainty)
    - Complexity level (simple vs complex)
    """

    config: QueryAnalysisConfig = QueryAnalysisConfig()

    async def prep_async(self, shared):
        """Prepare query and conversation history from shared store."""
        query = shared.get("query", "")
        conversation_history = shared.get("conversation_history", [])
        return query, conversation_history

    async def exec_async(self, inputs):
        """Classify query and extract key concepts using Groq."""
        query, conversation_history = inputs

        # Build context from conversation history
        context = ""
        if conversation_history:
            context = f"\n\nRecent conversation context:\n" + "\n".join(conversation_history[-3:])

        prompt = f"""Analyze this query and extract key information.

Query: "{query}"{context}

Provide a JSON response with these fields:
{{
  "query_type": "factual|rationale|summary|opinion|temporal",
  "key_concepts": ["concept1", "concept2", ...],
  "has_hedge_words": true/false,
  "complexity": "simple|complex",
  "extracted_entities": ["entity1", ...]
}}

Query types:
- factual: "When did I...?", "What is the...?", "Who is...?"
- rationale: "Why did I...?", "What was the reasoning for...?"
- summary: "Summarize...", "Give me an overview of..."
- opinion: "What do I think about...?", "How do I feel about...?"
- temporal: "What happened last week?", "What did I do in...?"

Return ONLY valid JSON, no markdown."""

        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.model_temperature,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Query analyzed: type={result.get('query_type')}, complexity={result.get('complexity')}")
            return result

        except Exception as e:
            logger.warning(f"Query analysis failed: {e}, using defaults")
            # Fallback to simple extraction
            concepts = [w for w in query.split() if len(w) > 3][:5]
            return {
                "query_type": "factual",
                "key_concepts": concepts,
                "has_hedge_words": any(hw in query.lower() for hw in self.config.hedge_words),
                "complexity": "simple",
                "extracted_entities": []
            }

    async def post_async(self, shared, prep_res, exec_res):
        """Store analysis results in shared store."""
        query, _ = prep_res
        shared["query_analysis"] = exec_res
        shared["original_query"] = query
        logger.debug(f"Query analysis complete: {exec_res}")
        return "default"


class HybridRetrievalNode(AsyncNode):
    """
    Retrieve relevant memories using hybrid keyword + semantic search.

    Searches across:
    - Content field
    - Entities
    - Observations

    Returns memories ordered by salience score.
    """

    config: HybridRetrievalConfig = HybridRetrievalConfig()

    async def prep_async(self, shared):
        """Prepare search terms from query analysis."""
        analysis = shared.get("query_analysis", {})
        query = shared.get("original_query", "")

        # Combine query with key concepts
        concepts = analysis.get("key_concepts", [])
        entities = analysis.get("extracted_entities", [])

        # Build search string from query + concepts + entities
        search_terms = [query]
        search_terms.extend(concepts)
        search_terms.extend(entities)

        return " ".join(search_terms)

    async def exec_async(self, inputs):
        """Execute hybrid search against Neo4j."""
        search_terms = inputs

        logger.debug(f"Executing hybrid retrieval for: '{search_terms}'")

        # Use keyword search (could be enhanced with semantic search)
        results = await search_bubbles(
            query=search_terms,
            limit=self.config.keyword_limit
        )

        # Filter by salience threshold
        filtered = [
            r for r in results
            if r.salience >= self.config.salience_threshold
        ]

        logger.info(f"Retrieved {len(filtered)} memories (salience >= {self.config.salience_threshold})")

        return filtered

    async def post_async(self, shared, prep_res, exec_res):
        """Store retrieved memories in shared store."""
        shared["retrieved_memories"] = exec_res
        shared["initial_result_count"] = len(exec_res)

        # Check if reflection is needed
        analysis = shared.get("query_analysis", {})
        complexity = analysis.get("complexity", "simple")

        if complexity == "complex" and len(exec_res) < ReflectionConfig.min_results_trigger:
            shared["need_reflection"] = True
            logger.info("Complex query with sparse results - reflection recommended")
        else:
            shared["need_reflection"] = False

        return "default"


class ReflectionNode(AsyncNode):
    """
    Optional reflection for complex queries with sparse results.

    Identifies information gaps and generates additional search concepts
    to retrieve supplementary memories.

    Uses OpenRouter for deep analysis (~2-5s).
    """

    config: ReflectionConfig = ReflectionConfig()

    async def prep_async(self, shared):
        """Check if reflection is needed and prepare context."""
        if not self.config.enabled:
            return None, False

        need_reflection = shared.get("need_reflection", False)
        if not need_reflection:
            return None, False

        query = shared.get("original_query", "")
        memories = shared.get("retrieved_memories", [])

        return query, memories, True

    async def exec_async(self, inputs):
        """Generate additional search concepts via reflection."""
        if not inputs[2]:  # Reflection not needed
            return []

        query, memories, _ = inputs

        # Format current memories for context
        memory_context = ""
        if memories:
            memory_context = "\n".join([
                f"- [{m.sector}] {m.content[:100]}..."
                for m in memories[:5]
            ])
        else:
            memory_context = "No memories found yet."

        prompt = f"""The user asked: "{query}"

Current search results:
{memory_context}

These results are insufficient. Identify 3-5 additional search concepts
that might help find relevant information. Consider:
- Synonyms and related terms
- Broader categories
- Alternative phrasings
- Related entities or people

Return ONLY a JSON list of strings:
["concept1", "concept2", "concept3", ...]"""

        try:
            client = get_openrouter_client()
            model = get_openrouter_model(self.config.model_task)

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )

            import json
            concepts = json.loads(response.choices[0].message.content)
            logger.info(f"Reflection generated {len(concepts)} additional concepts")
            return concepts

        except Exception as e:
            logger.warning(f"Reflection failed: {e}")
            return []

    async def post_async(self, shared, prep_res, exec_res):
        """Retrieve additional memories using reflection concepts."""
        concepts = exec_res

        if not concepts:
            shared["reflection_memories"] = []
            return "default"

        # Search for additional memories using reflection concepts
        all_additional = []
        for concept in concepts[:3]:  # Limit to 3 concepts
            results = await search_bubbles(query=concept, limit=5)
            all_additional.extend(results)

        # Remove duplicates (by ID)
        existing_ids = {m.id for m in shared.get("retrieved_memories", [])}
        additional = [m for m in all_additional if m.id not in existing_ids]

        shared["reflection_memories"] = additional
        shared["reflection_concepts"] = concepts

        logger.info(f"Reflection retrieved {len(additional)} additional memories")

        return "default"


class AnswerSynthesisNode(AsyncNode):
    """
    Synthesize final answer with reasoning and confidence.

    Generates:
    - Direct answer (2-4 sentences)
    - Reasoning trace with memory references [1], [2]
    - Confidence score (0.0-1.0)
    - Confidence label (Very Confident → Uncertain)

    Uses OpenRouter Creative model for synthesis (~2-5s).
    """

    config: AnswerSynthesisConfig = AnswerSynthesisConfig()

    async def prep_async(self, shared):
        """Prepare all retrieved memories for synthesis."""
        primary = shared.get("retrieved_memories", [])
        additional = shared.get("reflection_memories", [])

        # Combine all memories
        all_memories = primary + additional

        query = shared.get("original_query", "")
        analysis = shared.get("query_analysis", {})

        return query, analysis, all_memories

    async def exec_async(self, inputs):
        """Generate answer with reasoning and confidence."""
        query, analysis, memories = inputs

        if not memories:
            # No memories found - return helpful message
            return {
                "answer": "",
                "reasoning": self._no_results_message(query),
                "confidence": 0.0,
                "confidence_label": "No Results",
                "num_memories_used": 0
            }

        # Format memories for LLM
        memory_context = self._format_memories(memories)

        # Build synthesis prompt
        query_type = analysis.get("query_type", "factual")
        prompt = self._build_synthesis_prompt(query, query_type, memory_context)

        try:
            client = get_openrouter_client()
            model = get_openrouter_model(self.config.model_task)

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on memory data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            result = response.choices[0].message.content

            # Parse the response
            return self._parse_synthesis_result(result, memories)

        except Exception as e:
            logger.error(f"Answer synthesis failed: {e}")
            return {
                "answer": "I encountered an error generating the answer.",
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.0,
                "confidence_label": "Error",
                "num_memories_used": len(memories)
            }

    async def post_async(self, shared, prep_res, exec_res):
        """Store final result in shared store."""
        shared["final_result"] = exec_res

        answer = exec_res.get("answer", "")
        confidence = exec_res.get("confidence", 0.0)
        label = exec_res.get("confidence_label", "Unknown")

        logger.info(f"Answer synthesized: confidence={confidence:.2f} ({label})")

        return "default"

    def _format_memories(self, memories):
        """Format memories for LLM context."""
        formatted = []
        for i, m in enumerate(memories[:20], 1):  # Max 20 memories
            formatted.append(
                f"Memory [{i}]:\n"
                f"  ID: {m.id}\n"
                f"  Sector: {m.sector}\n"
                f"  Salience: {m.salience:.2f}\n"
                f"  Created: {m.created_at.strftime('%Y-%m-%d')}\n"
                f"  Content: {m.content}\n"
            )
        return "\n".join(formatted)

    def _build_synthesis_prompt(self, query, query_type, memory_context):
        """Build the synthesis prompt based on query type."""
        instructions = {
            "factual": "Provide a direct, factual answer to the question.",
            "rationale": "Explain the reasoning or rationale behind the decision/action.",
            "summary": "Provide a concise summary of the key points.",
            "opinion": "Describe the opinion, attitude, or feeling expressed.",
            "temporal": "Describe what happened during the time period in question."
        }

        instruction = instructions.get(query_type, instructions["factual"])

        return f"""Question: "{query}"

{instruction}

Available Memories:
{memory_context}

Provide your response in this exact format:

## Answer
[Your direct answer in 2-4 sentences]

## Reasoning
[Your reasoning trace, referencing memories like [1], [2], etc.]

## Confidence
[Your confidence score from 0.0 to 1.0, based on:
- 1.0: Direct evidence in memories, completely certain
- 0.8-0.9: Strong evidence, high confidence
- 0.6-0.7: Moderate evidence, some uncertainty
- 0.4-0.5: Limited evidence, tentative
- 0.3 or below: Very uncertain, speculation]

## Sources
[Number of memories used]
"""

    def _parse_synthesis_result(self, result, memories):
        """Parse the LLM response into structured result."""
        import re

        # Extract sections
        answer_match = re.search(r"## Answer\s*\n(.*?)(?=## Reasoning|$)", result, re.DOTALL)
        reasoning_match = re.search(r"## Reasoning\s*\n(.*?)(?=## Confidence|$)", result, re.DOTALL)
        confidence_match = re.search(r"## Confidence\s*\n(.*?)(?=## Sources|$)", result, re.DOTALL)

        answer = answer_match.group(1).strip() if answer_match else ""
        reasoning = reasoning_match.group(1).strip() if reasoning_match else result
        confidence_text = confidence_match.group(1).strip() if confidence_match else "0.5"

        # Extract confidence score
        score_match = re.search(r"([\d.]+)", confidence_text)
        confidence = float(score_match.group(1)) if score_match else 0.5

        # Determine confidence label
        confidence_label = self._get_confidence_label(confidence)

        return {
            "answer": answer,
            "reasoning": reasoning,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "num_memories_used": len(memories)
        }

    def _get_confidence_label(self, score):
        """Get human-readable confidence label."""
        if score >= 0.95:
            return "Very Confident"
        elif score >= 0.85:
            return "Confident"
        elif score >= 0.70:
            return "Moderately Confident"
        elif score >= 0.50:
            return "Somewhat Confident"
        elif score >= 0.30:
            return "Tentative"
        else:
            return "Uncertain"

    def _no_results_message(self, query):
        """Generate helpful message when no memories found."""
        return f"""No memories found matching your query: "{query}"

Suggestions:
1. Try rephrasing your question using different keywords
2. Use get_memory to search for specific terms
3. Use get_all_memories to see what you have stored
4. Check if the information exists in your memories using get_memory_relations"""


# Wire the flow
query_analysis_node = QueryAnalysisNode()
hybrid_retrieval_node = HybridRetrievalNode()
reflection_node = ReflectionNode()
answer_synthesis_node = AnswerSynthesisNode()

# Create flow with optional reflection
query_memories_flow = AsyncFlow(start=query_analysis_node)


# Convenience function for direct usage
async def query_memories(query: str, conversation_history: Optional[list] = None) -> dict:
    """
    Query memories with AI-powered answer synthesis.

    Args:
        query: Natural language question
        conversation_history: Optional list of recent messages for context

    Returns:
        Dictionary with answer, reasoning, confidence, and sources
    """
    shared = {
        "query": query,
        "conversation_history": conversation_history or [],
        "neo4j_driver": get_driver()
    }

    # Run the flow
    await query_analysis_node.exec_async((query, conversation_history))
    await hybrid_retrieval_node.exec_async(shared.get("query_analysis", {}).get("key_concepts", []))

    # Check if reflection needed
    if shared.get("need_reflection"):
        await reflection_node.exec_async((query, shared.get("retrieved_memories", [])))

    # Generate answer
    result = await answer_synthesis_node.exec_async((
        query,
        shared.get("query_analysis", {}),
        shared.get("retrieved_memories", [])
    ))

    return result
