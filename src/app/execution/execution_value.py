from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ExecutionValue:
    """
    Represents a value stored in the execution context,
    together with its provenance.
    """

    value: Any

    produced_by: str

    produced_at: datetime
