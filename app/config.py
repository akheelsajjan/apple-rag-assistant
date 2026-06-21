import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")

PINECONE_INDEX_NAME = "apple-rag-assistant"
PINECONE_CLOUD = "aws"
PINECONE_REGION = "us-east-1"
EMBEDDING_DIMENSION = 1536

LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
RETRIEVAL_K = 3

RERANK_MODEL = 'rerank-english-v3.0'
RERANK_TOP_N = 3
MAX_CLARIFICATION_RETRIES = 2

DATA_FILES = [
    {"path": "data/apple_inc.txt", "domain": "company"},
    {"path": "data/apple_fruit.txt", "domain": "fruit"},
]