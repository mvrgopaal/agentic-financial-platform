from app.rag.rag_chain import answer_question


def main():
    #question = "Which debts must be included in the qualifying ratio?"
    question = "You are an FHA underwriting assistant. \
		Use only the supplied mortgage guidelines. \
		If the answer is unavailable, \
		say you don't know. refer the chatGPT/Claude or any LLM data \
		Always cite the page.  \
		what is the FHA limit for maricopa county in arizona "


    print("\nQuestion:")
    print(question)

    answer = answer_question(question)

    print("\nRAG Answer:")
    print(answer)


if __name__ == "__main__":
    main()
