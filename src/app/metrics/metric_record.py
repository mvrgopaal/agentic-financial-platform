"""
Domain model representing one platform metric.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class MetricRecord:
    """
    One immutable metric captured during application execution.
    """

    name: str
    value: float
    unit: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    attributes: dict[str, Any] = field(
        default_factory=dict
    )
