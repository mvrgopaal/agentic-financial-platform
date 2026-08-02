"""
In-memory platform metrics collector.
"""

from typing import Any

from app.metrics.metric_record import MetricRecord


class MetricsCollector:
    """
    Collect metrics generated during one application request.

    This initial implementation stores metrics in memory.
    Future adapters may export them to Prometheus,
    CloudWatch, Datadog, or OpenTelemetry.
    """

    def __init__(self) -> None:
        self._records: list[MetricRecord] = []

    def record(
        self,
        name: str,
        value: float,
        unit: str,
        **attributes: Any,
    ) -> None:
        """
        Record one metric.
        """

        if not name.strip():
            raise ValueError(
                "Metric name cannot be empty."
            )

        if not unit.strip():
            raise ValueError(
                "Metric unit cannot be empty."
            )

        self._records.append(
            MetricRecord(
                name=name.strip(),
                value=float(value),
                unit=unit.strip(),
                attributes=dict(attributes),
            )
        )

    @property
    def records(self) -> tuple[MetricRecord, ...]:
        """
        Return an immutable view of collected metrics.
        """

        return tuple(self._records)

    def find(
        self,
        name: str,
    ) -> tuple[MetricRecord, ...]:
        """
        Return all metrics with the requested name.
        """

        return tuple(
            record
            for record in self._records
            if record.name == name
        )

    def clear(self) -> None:
        """
        Remove all collected metrics.
        """

        self._records.clear()
