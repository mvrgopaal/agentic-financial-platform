import faiss
from app.rag.retriever import load_vectorstore


print("Loading vectorstore")

vectorstore = load_vectorstore()

print("Loaded")

print(vectorstore.index.ntotal)

print("FAISS search test complete")
