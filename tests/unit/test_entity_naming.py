"""
Unit tests for entity_naming utility.

Phase 5.1: Basic Neo4j → Obsidian sync
"""

import pytest

from src.utils.entity_naming import slugify, generate_entity_name


class TestSlugify:
    """Test slugify function."""

    def test_simple_text(self):
        """Test slugifying simple text."""
        result = slugify("Chose PostgreSQL")
        assert result == "Chose_PostgreSQL"

    def test_with_multiple_words(self):
        """Test slugifying multiple words."""
        result = slugify("Met with FastTrack")
        assert result == "Met_with_FastTrack"

    def test_special_characters_removed(self):
        """Test that special characters are removed."""
        result = slugify("Hello@World#Test!")
        assert result == "HelloWorldTest"

    def test_hyphens_become_underscores(self):
        """Test that hyphens become underscores."""
        result = slugify("fast-track-project")
        assert result == "fast_track_project"

    def test_leading_trailing_underscores_removed(self):
        """Test that leading/trailing underscores are removed."""
        result = slugify("_test_")
        assert result == "test"

    def test_length_limit(self):
        """Test that slug is limited to 50 characters."""
        long_text = "A" * 100
        result = slugify(long_text)
        assert len(result) == 50
        assert result == "A" * 50

    def test_unicode_normalized(self):
        """Test that unicode is normalized."""
        result = slugify("café")
        assert result == "cafe"


class TestGenerateEntityName:
    """Test generate_entity_name function."""

    def test_single_entity_with_action(self):
        """Test single entity with detected action."""
        result = generate_entity_name(
            "Chose PostgreSQL over MongoDB for ACID compliance",
            ["PostgreSQL"],
            "Semantic"
        )
        assert "PostgreSQL" in result
        assert "Decision" in result or "Chose" in result

    def test_multiple_entities_with_action(self):
        """Test multiple entities with detected action."""
        result = generate_entity_name(
            "Chose PostgreSQL over MongoDB for ACID compliance",
            ["PostgreSQL", "MongoDB"],
            "Semantic"
        )
        assert "PostgreSQL" in result
        assert "MongoDB" in result or "Mongodb" in result
        assert ("Decision" in result or "Chose" in result or "Vs" in result)

    def test_single_entity_no_action(self):
        """Test single entity without detected action."""
        result = generate_entity_name(
            "PostgreSQL database stores user information",
            ["PostgreSQL"],
            "Semantic"
        )
        assert "PostgreSQL" in result
        assert "Sem" in result or "Sema" in result

    def test_no_entities_extract_from_content(self):
        """Test generating name when no entities provided."""
        result = generate_entity_name(
            "Meeting about project requirements",
            [],
            "Episodic"
        )
        assert len(result) > 0
        # Action "meeting" is detected, so it's used instead of sector prefix
        assert "Meeting" in result

    def test_meeting_action_detected(self):
        """Test that 'meeting' action is detected."""
        result = generate_entity_name(
            "Met with FastTrack client about N8N workflow",
            ["FastTrack"],
            "Episodic"
        )
        assert "FastTrack" in result
        assert "Meeting" in result or "Met" in result

    def test_deployed_action_detected(self):
        """Test that 'deployed' action is detected."""
        result = generate_entity_name(
            "Deployed new version to production",
            [],
            "Procedural"
        )
        assert "Deployed" in result

    def test_fallback_when_no_content(self):
        """Test fallback when content is minimal."""
        result = generate_entity_name(
            "Test",
            [],
            "Reflective"
        )
        assert "Memory" in result or "Ref" in result

    def test_sector_shortening(self):
        """Test that sector is shortened in name."""
        result = generate_entity_name(
            "Some content here",
            ["Entity"],
            "Procedural"
        )
        assert "Ent" in result
        # Should have sector prefix
        assert result.split("_")[-1] in ["Proc", "Pro", "Proce"]
