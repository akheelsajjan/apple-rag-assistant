from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.config import LLM_MODEL


class GradeDocument(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="Is this document relevant to the question? 'yes' or 'no'"
    )


def grade_document(question: str, document: str) -> str:
    llm = ChatOpenAI(model=LLM_MODEL)

    prompt = ChatPromptTemplate.from_template(
        "You are grading whether a retrieved document is relevant to a user question.\n\n"
        "Document: {document}\n\n"
        "Question: {question}\n\n"
        "If the document contains information that helps answer the question, grade 'yes'. "
        "Otherwise, grade 'no'. Be lenient — partial relevance counts as 'yes'."
    )

    structured_llm = llm.with_structured_output(GradeDocument)
    grader_chain = prompt | structured_llm

    result = grader_chain.invoke({"question": question, "document": document})
    return result.binary_score


def grade_documents(question: str, documents: list[str]) -> list[str]:
    """Filter a list of documents, keeping only those graded relevant."""
    relevant_docs = []
    for doc in documents:
        score = grade_document(question, doc)
        if score == "yes":
            relevant_docs.append(doc)
    return relevant_docs