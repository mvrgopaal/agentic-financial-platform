"""
Builds structured prompts for the LLM.
"""

from app.agents.prompt_definition import PromptDefinition
from app.execution.execution_context import ExecutionContext
from app.rag.retrieved_knowledge import RetrievedKnowledge


class PromptBuilder:
    """
    Converts execution results and retrieved knowledge
    into a structured prompt for an LLM.
    """

    def build(
        self,
        user_question: str,
        context: ExecutionContext,
        knowledge: RetrievedKnowledge,
    ) -> PromptDefinition:

        system_prompt = (
            "You are an experienced mortgage underwriter. "
            "Use only the supplied calculations and "
            "retrieved mortgage guidelines. "
            "Do not invent financial values."
        )

        context_summary = self._build_context_summary(
            context
        )

        reasoning_instructions = (
            "Base your reasoning only on the "
            "execution context and retrieved guidelines. "
            "If information is missing, clearly state it."
        )

        output_instructions = (
            "Provide:\n"
            "1. Qualification decision\n"
            "2. Supporting calculations\n"
            "3. Relevant guideline references\n"
            "4. Recommendations"
        )

        return PromptDefinition(
            system_prompt=system_prompt,
            user_prompt=user_question,
            context_summary=context_summary,
            retrieved_guidelines=[
                item.content
                for item in knowledge.items
            ],
            reasoning_instructions=reasoning_instructions,
            output_instructions=output_instructions,
        )

    def _build_context_summary(
        self,
        context: ExecutionContext,
    ) -> str:

        lines = []

        for key, value in sorted(context.values.items()):
            lines.append(f"{key}: {value}")

        return "\n".join(lines)
