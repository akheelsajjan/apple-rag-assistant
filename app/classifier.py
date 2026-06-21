from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.config import LLM_MODEL


class DomainClassification(BaseModel):
    domain: Literal["company", "fruit", "ambiguous", "irrelevant"] = Field(
        description=(
            "'company' if about Apple Inc the business/technology/products/finances. "
            "'fruit' if about apples as a fruit/botany/farming/cultivation. "
            "'ambiguous' if it could plausibly be either, using generic terms like yield, growth, market, production. "
            "'irrelevant' if the question has nothing to do with Apple Inc OR apples as fruit."
        )
    )


def classify_domain(question: str) -> str:
    llm = ChatOpenAI(model=LLM_MODEL)

    prompt = ChatPromptTemplate.from_template(
        "Classify this question into exactly one category: company, fruit, ambiguous, or irrelevant.\n\n"
        "Question: {question}"
    )

    structured_llm = llm.with_structured_output(DomainClassification)
    classifier_chain = prompt | structured_llm

    result = classifier_chain.invoke({"question": question})
    return result.domain