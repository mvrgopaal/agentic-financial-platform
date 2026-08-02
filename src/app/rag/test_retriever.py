from app.rag.retriever import search_documents

def main():
    print("1. Program started")

    question = "What is the maximum debt to income ratio?"

    print("2. Calling search_documents()")

    results = search_documents(question)

    print("3. Search completed")

    print(f"Retrieved {len(results)} document(s)")

    for i, doc in enumerate(results, start=1):
        print("=" * 60)
        print(f"Result {i}")
        print(doc.metadata)
        print(doc.page_content[:300])


if __name__ == "__main__":
    main()
