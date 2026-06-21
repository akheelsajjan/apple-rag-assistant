from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from app.graph import build_graph
from app.config import API_ACCESS_KEY

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Apple RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.29.154:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

graph = build_graph()
memory = MemorySaver()
compiled_graph = graph.compile(checkpointer=memory)


class ChatRequest(BaseModel):
    question: str
    thread_id: str
    is_clarification_reply: bool = False


class ChatResponse(BaseModel):
    status: str
    message: str
    thread_id: str
    domain: Optional[str] = None
    source: Optional[str] = None
    documents_used: Optional[int] = None
    average_relevance_score: Optional[float] = None


def verify_access_key(x_api_key: str = Header(...)):
    if x_api_key != API_ACCESS_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_access_key)])
def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    if request.is_clarification_reply:
        result = compiled_graph.invoke(Command(resume=request.question), config=config)
    else:
        result = compiled_graph.invoke({"question": request.question}, config=config)

    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value
        return ChatResponse(
            status="needs_clarification",
            message=interrupt_data["question"],
            thread_id=request.thread_id,
        )

    scores = result.get("document_scores", [])
    avg_score = sum(scores) / len(scores) if scores else None

    return ChatResponse(
        status="complete",
        message=result["answer"],
        thread_id=request.thread_id,
        domain=result.get("domain"),
        source=result.get("source", "local"),
        documents_used=len(result.get("documents", [])),
        average_relevance_score=round(avg_score, 3) if avg_score else None,
    )