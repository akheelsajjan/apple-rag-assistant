"use client";

import { useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim() === "" || disabled) return;

    onSend(text);
    setText("");
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t border-gray-200">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about Apple Inc. or apples..."
        disabled={disabled}
        className="flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded-full bg-blue-600 text-white px-6 py-2 text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300"
      >
        Send
      </button>
    </form>
  );
}