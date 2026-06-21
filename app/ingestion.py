from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
import uuid
from langchain_openai import OpenAIEmbeddings
from app.config import (
    DATA_FILES,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL
)



def load_documents():
    docs = []

    for file_config in DATA_FILES:
        with open(file_config["path"], "r", encoding="utf-8") as f:
            text_content = f.read()

        docs.append(
            Document(
                page_content=text_content,
                metadata={
                    "source": file_config["path"],
                    "domain": file_config["domain"],
                },
            )
        )

    return docs



def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    return chunks


def create_pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    if pc.has_index(PINECONE_INDEX_NAME):
        pc.delete_index(name=PINECONE_INDEX_NAME)

    pc.create_index(
        PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="dotproduct",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
    )

    index = pc.Index(PINECONE_INDEX_NAME)
    return index





def upload_chunks_to_pinecone(index, chunks):
    embedding_model = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]

    vectors_to_upsert = []
    for doc_id, chunk in zip(uuids, chunks):
        vector = embedding_model.embed_query(chunk.page_content)
        vectors_to_upsert.append({
            "id": doc_id,
            "values": vector,
            "metadata": {
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", ""),
                "domain": chunk.metadata.get("domain", ""),
            },
        })

    index.upsert(vectors=vectors_to_upsert)
    return uuids