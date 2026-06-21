# Apple RAG Assistant

A full-stack, domain-aware RAG application that answers questions about **Apple Inc.** (the company) and **apple** (the fruit) — two domains deliberately chosen because they share overlapping vocabulary ("growth," "yield," "market," "production"), making naive retrieval unreliable and creating a real testbed for advanced RAG techniques.

## What it does

- **Query routing** — an LLM classifies each question as `company`, `fruit`, `ambiguous`, or `irrelevant` before retrieval even happens.
- **Conversational clarification** — when a question is genuinely ambiguous (e.g. "what is the yield"), the assistant pauses mid-pipeline and asks the user to clarify, using LangGraph's human-in-the-loop `interrupt()`/`Command(resume=...)` pattern. Includes a retry limit with graceful fallback if the user stays vague.
- **Corrective RAG (CRAG)** — every retrieved document is graded for relevance by an LLM. If nothing relevant survives grading, the system automatically falls back to a live web search (Tavily) instead of answering from insufficient context.
- **Reranking** — Cohere's cross-encoder reranker refines the graded documents before generation, improving precision over vector search alone.
- **Conversation memory** — follow-up questions ("how about apple fruit?") are resolved using recent conversation history, not treated as isolated queries.
- **Transparent metadata** — the UI surfaces *how* each answer was produced: which domain it used, whether it came from local documents or a live web search, how many chunks contributed, and a numeric relevance score.

## Architecture

```
Next.js (TypeScript, Tailwind)
        │  POST /chat  { question, thread_id, is_clarification_reply }
        ▼
FastAPI backend
        │
        ▼
LangGraph state machine
   classify ──► retrieve ──► grade ──► rerank ──► generate
      │            │            │
      ▼            ▼            ▼
   clarify     (filtered    web_search
   (interrupt)  by domain)   (fallback)
      │
      ▼
  reclassify ──► (loop back to clarify, or proceed)
```

- **Vector store:** Pinecone (dense embeddings, metadata-filtered by domain)
- **Embeddings & LLM:** OpenAI (`text-embedding-3-small`, `gpt-4o-mini`)
- **Reranking:** Cohere `rerank-english-v3.0`
- **Web fallback:** Tavily Search API
- **Orchestration:** LangGraph (`StateGraph`, `MemorySaver` checkpointer, `interrupt`/`Command`)

## Why this dataset

Apple Inc. and apple-the-fruit share enough vocabulary that semantic search alone frequently confuses the two — a real, demonstrable case for query routing, conversational disambiguation, and metadata filtering, rather than a contrived example.

## Evaluation

Pipeline quality was measured with [RAGAS](https://github.com/explodinggradients/ragas) across 8 test questions spanning both domains:

| Metric | Score |
|---|---|
| Context Precision | 1.000 |
| Context Recall | 1.000 |
| Faithfulness | 0.979 |
| Answer Relevancy | 0.993 |

## Project structure

```
apple-rag-assistant/
├── app/                  # FastAPI backend + RAG pipeline
│   ├── config.py           # settings, API keys
│   ├── ingestion.py          # load, chunk, embed, upsert to Pinecone
│   ├── classifier.py           # domain classification
│   ├── retrieval.py              # Pinecone similarity search
│   ├── grading.py                  # CRAG relevance grading
│   ├── reranking.py                  # Cohere reranking
│   ├── web_search.py                   # Tavily fallback
│   ├── graph.py                          # LangGraph state machine
│   └── main_api.py                         # FastAPI app, /chat endpoint
├── ui/                   # Next.js frontend
│   ├── app/                 # pages, layout
│   ├── components/             # ChatMessage, ChatInput, MetadataSidebar, RelevanceBar
│   ├── lib/                      # API client
│   └── types/                      # shared TypeScript types
├── data/                 # source documents (Apple Inc. + apple fruit, Wikipedia-derived)
├── notebooks/            # exploratory development notebooks
└── pyproject.toml
```

## Running locally

**Backend:**
```bash
uv sync
uv run uvicorn app.main_api:app --reload
```

**Frontend:**
```bash
cd ui
npm install
npm run dev
```

Requires `.env` (backend) and `.env.local` (frontend) with: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `COHERE_API_KEY`, `TAVILY_API_KEY`, `API_ACCESS_KEY`.

## Tech stack

Python · FastAPI · LangChain · LangGraph · Pinecone · OpenAI · Cohere · Tavily · RAGAS · Next.js · TypeScript · Tailwind CSS
