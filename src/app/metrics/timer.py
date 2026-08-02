"""
Reusable execution timer for platform metrics.
"""

from time import perf_counter
from types import TracebackType
from typing import Any

from app.metrics.metrics_collector import MetricsCollector


class MetricTimer:
    """
    Context manager that records elapsed execution time.
    """

    def __init__(
        self,
        collector: MetricsCollector,
        metric_name: str,
        **attributes: Any,
    ) -> None:
        self.collector = collector
        self.metric_name = metric_name
        self.attributes = attributes
        self._started_at: float | None = None

    def __enter__(self) -> "MetricTimer":
        self._started_at = perf_counter()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if self._started_at is None:
            raise RuntimeError(
                "MetricTimer was not started."
            )

        duration_ms = (
            perf_counter() - self._started_at
        ) * 1000

        status = (
            "failed"
            if exception_type is not None
            else "success"
        )

        self.collector.record(
            name=self.metric_name,
            value=duration_ms,
            unit="milliseconds",
            status=status,
            **self.attributes,
        )

        # False means exceptions are not suppressed.
        return False
