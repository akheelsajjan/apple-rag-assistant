export interface ChatRequest {
  question: string;
  thread_id: string;
  is_clarification_reply?: boolean;
}

export interface ChatResponse {
  status: "complete" | "needs_clarification";
  message: string;
  thread_id: string;
  domain?: string | null;
  source?: string | null;
  documents_used?: number | null;
  average_relevance_score?: number | null;
}

export interface ChatMessageData {
  role: "user" | "assistant";
  content: string;
  metadata?: {
    domain?: string | null;
    source?: string | null;
    documents_used?: number | null;
    average_relevance_score?: number | null;
  };
}