"use client";
import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import MetadataSidebar from "@/components/MetadataSidebar";
import { sendMessage } from "@/lib/api";
import type { ChatMessageData, ChatResponse } from "@/types/chat";

export default function Home() {
  const [threadId] = useState<string>(() => uuidv4());
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [awaitingClarification, setAwaitingClarification] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  async function handleSend(userInput: string) {
    const userMessage: ChatMessageData = { role: "user", content: userInput };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage({
        question: userInput,
        thread_id: threadId,
        is_clarification_reply: awaitingClarification,
      });

      setAwaitingClarification(response.status === "needs_clarification");
      setLastResponse(response);

      const assistantMessage: ChatMessageData = {
        role: "assistant",
        content: response.message,
        metadata: {
          domain: response.domain,
          source: response.source,
          documents_used: response.documents_used,
          average_relevance_score: response.average_relevance_score,
        },
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessageData = {
        role: "assistant",
        content: "Something went wrong. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex h-screen">
      <div className="flex flex-col flex-1 max-w-3xl mx-auto">
        <header className="p-4 border-b border-gray-200">
          <h1 className="text-lg font-semibold">Apple RAG Assistant</h1>
          <p className="text-sm text-gray-500">
            Ask about Apple Inc. or apples (the fruit)
          </p>
        </header>

        <div className="flex-1 overflow-y-auto p-4">
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}
          {isLoading && <p className="text-sm text-gray-400">Thinking...</p>}
        </div>

        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>

      <MetadataSidebar
        domain={lastResponse?.domain}
        source={lastResponse?.source}
        documentsUsed={lastResponse?.documents_used}
        averageRelevanceScore={lastResponse?.average_relevance_score}
      />
    </div>
  );
}