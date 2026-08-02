"""
Validate that the local FAISS vector store exists
before retrieval begins.
"""

from pathlib import Path


class VectorStoreValidationError(RuntimeError):
    """
    Raised when required vector-store artifacts are missing.
    """


class VectorStoreValidator:
    """
    Validate the local FAISS vector-store artifacts.
    """

    def __init__(
        self,
        vectorstore_path: str = "data/vectorstore",
    ) -> None:
        self.vectorstore_path = Path(vectorstore_path)

    def validate(self) -> None:
        """
        Raise a clear error when the FAISS index is unavailable.
        """

        required_files = (
            self.vectorstore_path / "index.faiss",
            self.vectorstore_path / "index.pkl",
        )

        missing_files = [
            str(path)
            for path in required_files
            if not path.is_file()
        ]

        if missing_files:
            formatted_files = "\n".join(
                f"- {path}"
                for path in missing_files
            )

            raise VectorStoreValidationError(
                "The FAISS vector store is not ready.\n\n"
                "Missing required file(s):\n"
                f"{formatted_files}\n\n"
                "Rebuild the vector store from the project root:\n\n"
                "export KMP_DUPLICATE_LIB_OK=TRUE\n"
                "uv run python -m app.rag.test_vectorstore"
            )
