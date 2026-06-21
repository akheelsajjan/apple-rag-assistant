from langchain_cohere import CohereRerank
from langchain_core.documents import Document
from app.config import RERANK_MODEL, RERANK_TOP_N


def rerank_documents(question: str, documents: list[str]) -> list[str]:
    if not documents:
        return []

    reranker = CohereRerank(model=RERANK_MODEL, top_n=RERANK_TOP_N)

    docs_as_objects = [Document(page_content=text) for text in documents]

    reranked = reranker.compress_documents(
        documents=docs_as_objects,
        query=question,
    )

    return [
        {
            "text": doc.page_content,
            "score": doc.metadata.get("relevance_score", 0.0),
        }
        for doc in reranked
    ]