"""
One timed operation within a request trace.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class TraceSpan:
    """
    Represents one completed operation inside a trace.
    """

    trace_id: str
    name: str
    duration_ms: float
    status: str

    started_at: datetime
    completed_at: datetime

    attributes: dict[str, Any] = field(
        default_factory=dict
    )
