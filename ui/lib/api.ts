import type { ChatRequest, ChatResponse } from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        },
        body: JSON.stringify(request),
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data: ChatResponse = await response.json();
    return data;
}