from app.agents.local_mortgage_agent import run_agent


def main() -> None:
    questions = [
        (
            "My monthly debt is $3,400 and my gross monthly "
            "income is $8,000. Calculate my DTI."
        ),
        "Which debts must be included in the qualifying ratio?",
    ]

    for question in questions:
        print("=" * 80)
        print(f"QUESTION:\n{question}\n")

        try:
            answer = run_agent(question)
            print(f"ANSWER:\n{answer}\n")
        except Exception as exc:
            print(f"ERROR:\n{exc}\n")


if __name__ == "__main__":
    main()
