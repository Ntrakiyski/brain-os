"""
Entity name generation utility.
Creates readable, consistent filenames for Obsidian entities.

Phase 5.1: Basic Neo4j → Obsidian sync
"""

import re
import unicodedata
from typing import List


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    - Remove special characters
    - Replace spaces with underscores
    - Preserve original case (not title case)
    - Limit to 50 characters

    Examples:
        "Chose PostgreSQL" -> "Chose_PostgreSQL"
        "Met with FastTrack" -> "Met_With_FastTrack"
    """
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remove special characters (keep alphanumeric, spaces, underscores, hyphens)
    text = re.sub(r'[^\w\s-]', '', text)

    # Replace spaces and hyphens with underscores
    text = re.sub(r'[\s-]+', '_', text)

    # Remove leading/trailing underscores
    text = text.strip('_')

    # Limit to 50 characters
    return text[:50]


def generate_entity_name(
    content: str,
    entities: List[str],
    sector: str,
) -> str:
    """
    Generate a clean entity name for Obsidian file.

    Strategy:
    1. If entities provided: Use first entity + key action from content
    2. If no entities: Extract keywords from content + sector suffix
    3. Always sanitize and limit to 50 characters

    Args:
        content: Memory content
        entities: List of entity names
        sector: Cognitive sector (Semantic, Episodic, etc.)

    Returns:
        Sanitized entity name suitable for filename

    Examples:
        generate_entity_name(
            "Chose PostgreSQL over MongoDB for ACID compliance",
            ["PostgreSQL", "MongoDB"],
            "Semantic"
        )
        # Returns: "PostgreSQL_Vs_MongoDB_Decision"

        generate_entity_name(
            "Met with FastTrack client about N8N workflow",
            ["FastTrack"],
            "Episodic"
        )
        # Returns: "FastTrack_N8n_Workflow_Meeting"
    """
    # Extract action verbs and key nouns from content
    action_words = ["decision", "chose", "selected", "meeting", "met", "discussed",
                   "deployed", "implemented", "learned", "discovered"]

    content_lower = content.lower()
    detected_action = None
    for action in action_words:
        if action in content_lower:
            detected_action = action.title()
            break

    if entities:
        # Use first entity + action/sector
        primary_entity = slugify(entities[0])

        if len(entities) > 1:
            # Multiple entities: "Entity1_vs_Entity2_Decision"
            secondary_entity = slugify(entities[1])
            if detected_action:
                return f"{primary_entity}_vs_{secondary_entity}_{detected_action}"
            return f"{primary_entity}_and_{secondary_entity}_{sector[:3]}"
        else:
            # Single entity: "Entity_Action" or "Entity_Sector"
            if detected_action:
                return f"{primary_entity}_{detected_action}"
            return f"{primary_entity}_{sector[:4]}"
    else:
        # No entities: Extract from content
        words = content.split()
        # First 2-3 meaningful words
        keywords = [w for w in words if len(w) > 3][:3]
        prefix = "_".join(slugify(k) for k in keywords)

        if detected_action:
            return f"{prefix}_{detected_action}"
        return f"{prefix}_{sector[:3]}"

    # Fallback
    return f"Memory_{sector[:3]}"
