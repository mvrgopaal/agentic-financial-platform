from app.llm import llm
from app.rag.retriever import search_documents


SYSTEM_PROMPT = """
You are a mortgage underwriting assistant.

Answer the user's question using only the supplied mortgage-guideline context.

Rules:
1. Do not invent rules or thresholds.
2. If the context is insufficient, say that the available documents do not provide enough information.
3. Cite the source and page label when available.
4. Clearly distinguish guideline language from your own explanation.
"""


def format_context(documents) -> str:
    sections = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get(
            "page_label",
            document.metadata.get("page", "Unknown page"),
        )

        sections.append(
            f"[Source {index}]\n"
            f"File: {source}\n"
            f"Page: {page}\n"
            f"Content:\n{document.page_content}"
        )

    return "\n\n".join(sections)


def answer_question(question: str, k: int = 5) -> str:
    documents = search_documents(question, k=k)
    context = format_context(documents)

    messages = [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            f"""
Mortgage-guideline context:

{context}

Question:
{question}
""",
        ),
    ]

    response = llm.invoke(messages)
    return response.content
