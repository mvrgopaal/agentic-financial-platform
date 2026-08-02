"""
Request-level tracing context.
"""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class TraceContext:
    """
    Identifies one end-to-end platform request.
    """

    trace_id: str = field(
        default_factory=lambda: str(uuid4())
    )
