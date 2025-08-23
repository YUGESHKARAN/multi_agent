

import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import BaseMessage

# Load environment variables
load_dotenv()

# -------------------- Mongo Agent Import --------------------
from agents.mongo_agent import response_generator, db

# -------------------- Pinecone Agent Import --------------------
from agents.pinecone_agent import query_documents

# -------------------- LLM Router Setup --------------------
from langchain_groq import ChatGroq

llm_router = ChatGroq(model="llama-3.3-70b-versatile")

router_prompt = PromptTemplate.from_template("""
You are a tool router. Your job is to pick one tool name only.

Available tools:
- "product_agent": For user data, products, inserting or updating MongoDB entries.
- "pinecone_agent": For questions about documents or needing RAG over uploaded documents.

ONLY return one word: "product_agent" or "pinecone_agent". No explanation.

Question: {question}
Tool:
""")

router_chain = router_prompt | llm_router | StrOutputParser()

# -------------------- Define State --------------------
class AppState(BaseModel):
    question: str
    email: str
    chat_history: Optional[List[BaseMessage]] = []
    answer: Optional[str] = None
    route: Optional[str] = None

# -------------------- Router Function --------------------
def router_fn(state: AppState) -> dict:
    tool = router_chain.invoke({"question": state.question})
    return {"route": tool.strip().lower()}

# -------------------- Mongo Agent as Runnable --------------------
def mongo_agent(state: AppState)-> dict:

    return {"answer": response_generator(
        user_query=state.question,
        email=state.email,
        db=db,
        chat_history=state.chat_history or []
    )}

# -------------------- Pinecone_agent Agent as Runnable --------------------
def pinecone_agent(state: AppState) -> dict:
     return {"answer": query_documents(state.question)}
    


# -------------------- Graph Assembly --------------------
graph = StateGraph(AppState)

graph.add_node("supervisor", router_fn)
graph.add_node("product_agent", mongo_agent)
graph.add_node("pinecone_agent", pinecone_agent)

graph.set_entry_point("supervisor")

# ✅ Correct usage: use router_fn as second arg (not string)
graph.add_conditional_edges(
    "supervisor",
    lambda state: state.route,  # use the route field
    {
        "product_agent": "product_agent",
        "pinecone_agent": "pinecone_agent"
    }
)

graph.add_edge("product_agent", END)
graph.add_edge("pinecone_agent", END)

# -------------------- Compile Graph --------------------
app_graph = graph.compile()
