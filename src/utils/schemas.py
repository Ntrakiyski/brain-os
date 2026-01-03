"""
Pydantic schemas for data validation in Brain OS.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BubbleCreate(BaseModel):
    """Schema for creating a new memory bubble."""
    content: str = Field(..., min_length=1, description="The memory content")
    sector: str = Field(..., description="Cognitive sector (Episodic, Semantic, Procedural, Emotional, Reflective)")
    source: str = Field(default="direct_chat", description="Origin of the data (transcript, direct_chat, etc.)")
    salience: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score (0.0 to 1.0)")

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        """Validate that sector is one of the five cognitive sectors."""
        valid_sectors = {"Episodic", "Semantic", "Procedural", "Emotional", "Reflective"}
        v_capitalized = v.capitalize()
        if v_capitalized not in valid_sectors:
            raise ValueError(f"sector must be one of: {', '.join(valid_sectors)}")
        return v_capitalized


class BubbleResponse(BaseModel):
    """Schema for a memory bubble response from the database.

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
