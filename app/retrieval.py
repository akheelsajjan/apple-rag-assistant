from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from app.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL, RETRIEVAL_K


def get_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)


def retrieve_documents(question: str, domain: str) -> list[str]:
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    index = get_index()

    query_vector = embedding_model.embed_query(question)

    results = index.query(
        vector=query_vector,
        top_k=RETRIEVAL_K,
        filter={"domain": domain},
        include_metadata=True,
    )

    documents = [match["metadata"]["text"] for match in results["matches"]]
    return documents