from loader import load_pdf
from splitter import split_documents


pdf_path = "data/documents/mortgage_guidelines.pdf"


documents = load_pdf(pdf_path)

chunks = split_documents(documents)


print("Original pages:", len(documents))

print("Total chunks:", len(chunks))


print("\nFirst chunk:")
print(chunks[0].page_content[:500])


print("\nMetadata:")
print(chunks[0].metadata)
