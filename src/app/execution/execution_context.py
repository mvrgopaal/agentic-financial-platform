from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionContext:
    """
    Shared state available to all executing tools.
    """

    values: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any:
        return self.values.get(key)

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def update(self, outputs: dict[str, Any]) -> None:
        self.values.update(outputs)

    def contains(self, key: str) -> bool:
        return key in self.values

    def __str__(self) -> str:
        return str(self.values)
