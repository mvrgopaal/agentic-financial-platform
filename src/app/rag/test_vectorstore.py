from app.rag.loader import load_pdf
from app.rag.splitter import split_documents
from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import create_vectorstore


pdf_path = "data/documents/mortgage_guidelines.pdf"


print("Loading PDF...")
documents = load_pdf(pdf_path)


print("Splitting documents...")
chunks = split_documents(documents)


print("Creating embeddings...")
embeddings = create_embeddings()


print("Creating FAISS database...")
vectorstore = create_vectorstore(
    chunks,
    embeddings
)


print("FAISS database created successfully!")
