# run.py

from langgraph_app import app_graph

def main():
    chat_history = []
    while True:
        q = input("User: ").strip()
        if not q or q.lower() in ("exit", "quit"):
            break
        email = input("Email: ").strip()

        result = app_graph.invoke({
            "question": q,
            "email": email,
            "chat_history": chat_history
        })
        print("\nBot:", result["answer"], "\n")
        chat_history.append(q)

if __name__ == "__main__":
    main()
