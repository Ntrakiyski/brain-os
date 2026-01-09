"""
Pydantic schemas for data validation in Brain OS.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class MemoryType(str):
    """Memory type classification for Phase 3."""
    INSTINCTIVE = "instinctive"
    THINKING = "thinking"
    DORMANT = "dormant"


class BubbleCreate(BaseModel):
    """Schema for creating a new memory bubble.

    Phase 3 Enhanced: Supports memory_type, activation_threshold, entities, and observations.
    """
    content: str = Field(..., min_length=1, description="The memory content")
    sector: str = Field(..., description="Cognitive sector (Episodic, Semantic, Procedural, Emotional, Reflective)")
    source: str = Field(default="direct_chat", description="Origin of the data (transcript, direct_chat, etc.)")
    salience: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score (0.0 to 1.0)")

    # Phase 3 fields
    memory_type: Literal["instinctive", "thinking", "dormant"] = Field(
        default="thinking",
        description="Memory type: 'instinctive' (auto-activates), 'thinking' (explicit recall), or 'dormant' (low priority)"
    )
    activation_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Activation threshold (0.0-1.0). Auto-calculated from memory_type if None."
    )
    entities: list[str] = Field(
        default_factory=list,
        description="Named entities mentioned (e.g., ['Project A', 'FastAPI'])"
    )
    observations: list[str] = Field(
        default_factory=list,
        description="Specific facts/observations (e.g., ['Chosen for async support'])"
    )

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        """Validate that sector is one of the five cognitive sectors."""
        valid_sectors = {"Episodic", "Semantic", "Procedural", "Emotional", "Reflective"}
        v_capitalized = v.capitalize()
        if v_capitalized not in valid_sectors:
            raise ValueError(f"sector must be one of: {', '.join(valid_sectors)}")
        return v_capitalized

    @field_validator("activation_threshold")
    @classmethod
    def calculate_threshold_if_none(cls, v: Optional[float], info) -> Optional[float]:
        """Auto-calculate activation_threshold based on memory_type if not provided."""
        if v is not None:
            return v

        # Get memory_type from the validation info
        memory_type = info.data.get("memory_type", "thinking")

        # Auto-calculate based on memory type
        thresholds = {
            "instinctive": 0.25,  # Auto-activates easily
            "thinking": 0.65,     # Requires explicit intent
            "dormant": 0.90,      # Rarely surfaces
        }
        return thresholds.get(memory_type, 0.65)


class BubbleResponse(BaseModel):
    """Schema for a memory bubble response from the database.

    Phase 3 Enhanced: Includes memory_type, activation_threshold, entities, observations.

    Note: Neo4j element_id is returned as a string (e.g., '4:uuid:0').
    """
    id: str
    content: str
    sector: str
    source: str
    salience: float
    created_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime] = None

    # Phase 3 fields
    memory_type: Optional[Literal["instinctive", "thinking", "dormant"]] = None
    activation_threshold: Optional[float] = None
    entities: Optional[list[str]] = None
    observations: Optional[list[str]] = None
    accessed_count: Optional[int] = None
    last_accessed: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MemorySearchParams(BaseModel):
    """Schema for memory search parameters."""
    query: str = Field(..., min_length=1, description="Search keyword")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return")


class MemorySearchResult(BaseModel):
    """Schema for memory search results."""
    bubbles: list[BubbleResponse]
    total_count: int
    query: str
