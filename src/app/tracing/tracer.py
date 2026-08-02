"""
In-memory enterprise request tracer.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterator

from app.tracing.trace_context import TraceContext
from app.tracing.trace_span import TraceSpan


class Tracer:
    """
    Collect timed spans for one request trace.

    This in-memory implementation can later be replaced or
    extended with OpenTelemetry, LangSmith, Datadog, or Zipkin.
    """

    def __init__(
        self,
        context: TraceContext | None = None,
    ) -> None:
        self.context = context or TraceContext()
        self._spans: list[TraceSpan] = []

    @property
    def trace_id(self) -> str:
        return self.context.trace_id

    @property
    def spans(self) -> tuple[TraceSpan, ...]:
        """
        Return an immutable view of completed spans.
        """

        return tuple(self._spans)

    @contextmanager
    def span(
        self,
        name: str,
        **attributes: Any,
    ) -> Iterator[None]:
        """
        Measure and record one operation within the trace.
        """

        if not name.strip():
            raise ValueError(
                "Trace span name cannot be empty."
            )

        started_at = datetime.now(timezone.utc)
        started_counter = perf_counter()
        status = "success"

        try:
            yield

        except Exception:
            status = "failed"
            raise

        finally:
            completed_at = datetime.now(timezone.utc)

            duration_ms = (
                perf_counter() - started_counter
            ) * 1000

            self._spans.append(
                TraceSpan(
                    trace_id=self.trace_id,
                    name=name.strip(),
                    duration_ms=duration_ms,
                    status=status,
                    started_at=started_at,
                    completed_at=completed_at,
                    attributes=dict(attributes),
                )
            )
