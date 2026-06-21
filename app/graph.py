from typing import Optional, List, Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

from app.classifier import classify_domain
from app.retrieval import retrieve_documents
from app.grading import grade_documents
from app.reranking import rerank_documents
from app.web_search import web_search
from app.config import LLM_MODEL, MAX_CLARIFICATION_RETRIES


# --- State ---

class RAGState(BaseModel):
    question: str
    domain: Optional[Literal["company", "fruit", "ambiguous", "irrelevant"]] = None
    clarification_answer: Optional[str] = None
    retry_count: int = 0
    documents: List[str] = []
    answer: str = ""
    document_scores: List[float] = []     
    source: str = "local"                   
    web_search_needed: bool = False
    conversation_history: List[dict] = []


# --- Nodes ---

def classify_node(state: RAGState) -> RAGState:
    history_context = ""
    if state.conversation_history:
        last_turn = state.conversation_history[-1]
        history_context = f"Previous question: {last_turn['question']}\n"

    combined_question = f"{history_context}Current question: {state.question}"
    state.domain = classify_domain(combined_question)
    return state

def retrieve_node(state: RAGState) -> RAGState:
    state.documents = retrieve_documents(state.question, state.domain)
    return state


def grade_node(state: RAGState) -> RAGState:
    relevant_docs = grade_documents(state.question, state.documents)
    state.documents = relevant_docs
    state.web_search_needed = len(relevant_docs) == 0
    return state


def rerank_node(state: RAGState) -> RAGState:
    reranked = rerank_documents(state.question, state.documents)
    state.documents = [item["text"] for item in reranked]
    state.document_scores = [item["score"] for item in reranked]
    return state


def web_search_node(state: RAGState) -> RAGState:
    state.documents = web_search(state.question)
    state.source = "web"
    return state


def generate_node(state: RAGState) -> RAGState:
    llm = ChatOpenAI(model=LLM_MODEL)
    context = "\n\n".join(state.documents)

    history_text = ""
    for turn in state.conversation_history[-3:]:
        history_text += f"Q: {turn['question']}\nA: {turn['answer']}\n\n"

    prompt = (
        f"Previous conversation:\n{history_text}\n"
        f"Context:\n{context}\n\n"
        f"Current question: {state.question}\n\n"
        f"Answer the current question, using the previous conversation to understand "
        f"references like 'it', 'that', or follow-up phrasing like 'how about X'."
    )

    response = llm.invoke(prompt)
    state.answer = response.content

    state.conversation_history.append({"question": state.question, "answer": state.answer})

    return state


def clarify_node(state: RAGState) -> RAGState:
    user_response = interrupt({
        "question": "Are you asking about Apple Inc. (the company) or apple (the fruit)?"
    })
    state.clarification_answer = user_response
    return state


def reclassify_node(state: RAGState) -> RAGState:
    combined = f"Original question: {state.question}\nUser clarified: {state.clarification_answer}"
    state.domain = classify_domain(combined)
    state.retry_count += 1
    return state


def decline_node(state: RAGState) -> RAGState:
    state.answer = "I can only answer questions about Apple Inc. (the company) or apples (the fruit)."
    return state


def give_up_node(state: RAGState) -> RAGState:
    state.answer = "I couldn't understand which Apple you mean. Could you rephrase your question?"
    return state


# --- Routers ---

def route_after_classify(state: RAGState) -> str:
    if state.domain == "irrelevant":
        return "decline"
    elif state.domain == "ambiguous":
        return "clarify"
    else:
        return "retrieve"


def route_after_reclassify(state: RAGState) -> str:
    if state.domain == "irrelevant":
        return "decline"
    elif state.domain in ("company", "fruit"):
        return "retrieve"
    elif state.retry_count >= MAX_CLARIFICATION_RETRIES:
        return "give_up"
    else:
        return "clarify"


def route_after_grading(state: RAGState) -> str:
    if state.web_search_needed:
        return "web_search"
    else:
        return "generate"


# --- Graph assembly ---

def build_graph():
    graph = StateGraph(RAGState)

    graph.add_node("classify", classify_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("reclassify", reclassify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("generate", generate_node)
    graph.add_node("decline", decline_node)
    graph.add_node("give_up", give_up_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {"decline": "decline", "clarify": "clarify", "retrieve": "retrieve"}
    )

    graph.add_edge("clarify", "reclassify")

    graph.add_conditional_edges(
        "reclassify",
        route_after_reclassify,
        {"decline": "decline", "retrieve": "retrieve", "give_up": "give_up", "clarify": "clarify"}
    )

    graph.add_edge("retrieve", "grade")

    graph.add_conditional_edges(
        "grade",
        route_after_grading,
        {"web_search": "web_search", "generate": "rerank"}
    )

    graph.add_edge("web_search", "generate")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)
    graph.add_edge("decline", END)
    graph.add_edge("give_up", END)

    return graph