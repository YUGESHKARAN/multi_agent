from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import AIMessage, HumanMessage

# from langsmith import traceable

from langgraph_app import app_graph

app = Flask(__name__)

CORS(app)

chat_history = []

@app.route("/")
def welcome_blog_backend():
    return "Welcome to Agentic AI"

@app.route("/query-multiagent", methods=['POST'])
def main():
    data = request.json
    user_query = data.get("query", "")
    chat_history.append(HumanMessage(content=user_query))
    user_email = data.get("email", "")

    if user_query:
        response = app_graph.invoke({
            "question": user_query,
            "email": user_email,
            "chat_history": chat_history
        })

        if response:
            answer = response.get("answer", "")
            chat_history.append(AIMessage(content=answer))
            return jsonify({"response": answer})

    return jsonify({"response": "No query received"})

if __name__ == "__main__":
    app.run(port=4500, host="0.0.0.0", debug=False)



