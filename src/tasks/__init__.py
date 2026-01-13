"""
Background Tasks for Brain OS.

Phase 4: Circadian rhythm - automated maintenance cycles.
"""

from src.tasks.background import (
    synaptic_pruning_task,
    cloud_synthesis_task,
    health_check_task,
    TASK_REGISTRY,
    get_all_task_status,
    get_task_status_by_name
)

__all__ = [
    "synaptic_pruning_task",
    "cloud_synthesis_task",
    "health_check_task",
    "TASK_REGISTRY",
    "get_all_task_status",
    "get_task_status_by_name"
]
