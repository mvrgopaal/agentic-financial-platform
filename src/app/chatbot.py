from .llm import llm

def chat():
   
    print("Financial AI Advisor")
    print("Type 'quit' to exit\n")


while True:
    question = input("You: ")

    if question.lower() == "quit":
        break

    answer = llm.invoke(question)

    print(answer.content)
    print()

if __name__ == "__main__":
   chat()
