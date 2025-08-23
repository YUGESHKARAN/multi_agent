# run.py

from langgraph_app import app_graph
from IPython.display import Image, display

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
    # main()

    img_bytes = app_graph.get_graph().draw_mermaid_png()
    with open("igraph.png", "wb") as f:
        f.write(img_bytes)
    print("Graph saved as graph.png")


