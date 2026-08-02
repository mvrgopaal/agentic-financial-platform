"""
Structured prompt exchanged between the
Financial Agent and the LLM.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class PromptDefinition:
    """
    Represents the complete prompt sent to an LLM.

    Each section has a single responsibility.
    """

    system_prompt: str

    user_prompt: str

    context_summary: str

    retrieved_guidelines: list[str] = field(
        default_factory=list
    )

    reasoning_instructions: str = ""

    output_instructions: str = ""
