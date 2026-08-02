from app.rag.embeddings import create_embeddings


embeddings = create_embeddings()


text = "FHA loans allow higher debt to income ratios."


vector = embeddings.embed_query(text)


print("Vector size:", len(vector))

print("First 10 values:")
print(vector[:10])
