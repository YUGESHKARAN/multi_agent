# langgraph_app.py

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage
from typing import List, Optional, Union

load_dotenv()

# ─── Imports ────────────────────────────────────────────────────────────────────
from agents.mongo_agent import response_generator, db
from agents.pinecone_agent import query_documents
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


# ─── Router LLM Setup ─────────────────────────────────────────────────────────
# llm_router = ChatGroq(model="llama-3.3-70b-versatile")
llm_router = ChatOpenAI(model_name="gpt-4.1")
router_prompt = PromptTemplate.from_template("""
You are a tool router. Pick exactly one tool name: "mongo" or "pinecone".

- mongo: product/user DB CRUD
- pinecone: document-based RAG

Return exactly one word and nothing else.

Question: {question}
Tool:
""")
router_chain = router_prompt | llm_router | StrOutputParser()

# ─── State Schema ──────────────────────────────────────────────────────────────
class AppState(BaseModel):
    question: str
    email: str
    chat_history: Optional[List[Union[HumanMessage, AIMessage]]] = []

    answer: Optional[str] = None

# ─── Master Node (router + agents) ─────────────────────────────────────────────
def master_fn(state: AppState):
    tool = router_chain.invoke({"question": state.question}).strip().lower()
    if tool == "mongo":
        out = response_generator(
            user_query=state.question,
            email=state.email,
            db=db,
            chat_history=state.chat_history or []
        )
    else:  # pinecone
        out = query_documents(state.question)
    return {"answer": out}

master_node = RunnableLambda(master_fn)

# ─── Graph Assembly ────────────────────────────────────────────────────────────
graph = StateGraph(AppState)
graph.add_node("master", master_node)
graph.set_entry_point("master")
graph.add_edge("master", END)

app_graph = graph.compile()
