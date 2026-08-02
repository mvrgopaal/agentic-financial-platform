from pathlib import Path

from langchain_community.vectorstores import FAISS

from app.rag.embeddings import create_embeddings


VECTOR_DB_PATH = Path("data/vectorstore")


def load_vectorstore():
    """
    Load the FAISS vector database from disk.
    """

    embeddings = create_embeddings()

    vectorstore = FAISS.load_local(
        folder_path=str(VECTOR_DB_PATH),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore


def get_retriever(k: int = 5):
    """
    Create a retriever that returns the top-k most
    relevant document chunks.
    """

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever


def search_documents(question: str, k: int = 5):
    print("A. Loading vectorstore")
    vectorstore = load_vectorstore()

    print("B. Vectorstore loaded")

    print("C. Running similarity search")
    results = vectorstore.similarity_search(question, k=k)

    print("D. Similarity search finished")

    return results

