from loader import load_pdf


pdf_path = "data/documents/mortgage_guidelines.pdf"


documents = load_pdf(pdf_path)


print(f"Number of pages: {len(documents)}")

print("\nFirst page content:")
print(documents[0].page_content[:1000])

print("\nMetadata:")
print(documents[0].metadata)
