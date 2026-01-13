"""
Memory creation tool.
Stores new bubbles in the Synaptic Graph.

Phase 4 Enhancement: Added enhanced logging.
"""

import logging
from pydantic import Field

from src.database.queries.memory import upsert_bubble
from src.utils.schemas import BubbleCreate

logger = logging.getLogger(__name__)


def register_create_memory(mcp) -> None:
    """Register the create_memory tool with FastMCP."""

    @mcp.tool
    async def create_memory(
        content: str = Field(
            description="What to remember. Include WHY, not just WHAT (e.g., 'Chose PostgreSQL over MongoDB for ACID compliance' not just 'Use PostgreSQL')"
        ),
        sector: str = Field(
            description="Cognitive sector. REQUIRED - Choose from: Episodic (events/meetings), Semantic (facts/decisions), Procedural (how-to/workflows), Emotional (feelings/reactions), Reflective (insights/learnings)"
        ),
        source: str = Field(
            default="direct_chat",
            description="Origin of data. Examples: meeting, transcript, technical_decision, direct_chat, email, documentation",
        ),
        salience: float = Field(
            default=0.5,
            ge=0.0,
            le=1.0,
            description="Importance score (0.0-1.0). Use the full range: 0.9-1.0 (business-critical), 0.7-0.8 (important), 0.5-0.6 (routine), 0.3-0.4 (nice-to-know), 0.0-0.2 (temporary)"
        ),
        # Phase 3 parameters
        memory_type: str = Field(
            default="thinking",
            description="Memory activation pattern: 'instinctive' (auto-activates like a hot oven - use sparingly for decisions/pricing/procedures), 'thinking' (explicit recall - default), 'dormant' (archives)"
        ),
        activation_threshold: float = Field(
            default=None,
            description="Auto-calculated if omitted. Override only if you need custom auto-activation sensitivity: 0.25 (easy activation), 0.65 (moderate), 0.90 (rare)"
        ),
        entities: list[str] = Field(
            default=[],
            description="Key entities for retrieval: people, projects, technologies. Keep names consistent across memories (e.g., always 'FastTrack' not 'fast track')"
        ),
        observations: list[str] = Field(
            default=[],
            description="Additional context that supports but isn't the main point: rationale, trade-offs, deadlines, criteria, what was considered"
        ),
    ) -> str:
        """
        Store a new memory in the Synaptic Graph.

        **Use this for ANY information worth remembering.**

        Best Practices:
        - Include decision rationale in observations, not just content
        - Use consistent entity names across memories (e.g., always "FastTrack" not "fast track")
        - Set appropriate salience - don't default everything to 0.5
        - Only mark truly auto-relevant memories as instinctive

        Common Patterns:

        **Decision** (Semantic + instinctive + high salience):
        - content: "Chose PostgreSQL over MongoDB for ACID compliance"
        - observations: ["Financial data requires transactions", "Regulatory compliance needed"]
        - salience: 0.8

        **Meeting** (Episodic + thinking + medium salience):
        - content: "FastTrack client meeting: Discussed N8N workflow scope"
        - observations: ["Budget: 20 hours approved", "Start: Monday Jan 12", "Rate: €60/hour"]
        - salience: 0.6

        **Procedure** (Procedural + instinctive + high salience):
        - content: "Deployment: Use docker compose up -d for production"
        - observations: ["Must pull latest images first", "Check logs with docker logs"]
        - salience: 0.7
        """
        try:
            # Phase 4: Enhanced logging
            logger.debug(f"create_memory: Starting memory creation for sector '{sector}'")
            logger.info(f"Creating {sector} memory (type: {memory_type}, salience: {salience})")

            # Validate and create the bubble
            bubble_data = BubbleCreate(
                content=content,
                sector=sector,
                source=source,
                salience=salience,
                memory_type=memory_type,
                activation_threshold=activation_threshold,
                entities=entities,
                observations=observations,
            )
            result = await upsert_bubble(bubble_data)

            logger.info(
                f"Memory stored successfully: ID={result.id}, Sector={result.sector}, "
                f"Salience={result.salience}, Type={memory_type}"
            )

            # Phase 5.1: Sync to Obsidian (if configured)
            obsidian_sync_result = ""
            try:
                from src.utils.obsidian_client import sync_to_obsidian
                from src.utils.entity_naming import generate_entity_name

                entity_name = generate_entity_name(
                    content=content,
                    entities=entities,
                    sector=sector,
                )

                obsidian_metadata = {
                    "salience": salience,
                    "memory_type": memory_type,
                    "neo4j_id": str(result.id),
                    "created": result.created_at.isoformat(),
                    "source": source,
                    "sector": sector,
                }

                sync_success = await sync_to_obsidian(
                    entity_name=entity_name,
                    entity_type=sector,
                    content=content,
                    observations=observations,
                    metadata=obsidian_metadata,
                )

                if sync_success:
                    obsidian_sync_result = f"\n- Obsidian: {entity_name}.md"
                    logger.info(f"Successfully synced to Obsidian: {entity_name}")
                else:
                    obsidian_sync_result = "\n⚠️ Obsidian sync: Unavailable (Neo4j stored)"
                    logger.warning(f"Obsidian sync failed for memory {result.id}")

            except ImportError:
                # Obsidian utilities not available - skip sync
                logger.debug("Obsidian client not available, skipping sync")
            except Exception as e:
                # Obsidian sync failed - don't fail the entire operation
                logger.warning(f"Obsidian sync error: {e}")
                obsidian_sync_result = "\n⚠️ Obsidian sync: Failed (Neo4j stored)"

            return (
                f"Memory stored successfully!{obsidian_sync_result}\n"
                f"- Neo4j ID: {result.id}\n"
                f"- Sector: {result.sector}\n"
                f"- Created: {result.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"- Salience: {result.salience}\n"
                f"- Content: {result.content[:100]}{'...' if len(result.content) > 100 else ''}"
            )
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            return f"Error storing memory: {str(e)}"
