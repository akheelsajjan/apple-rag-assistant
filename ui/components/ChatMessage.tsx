import type { ChatMessageData } from "@/types/chat";

interface ChatMessageProps {
    message: ChatMessageData;
}

export default function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === "user";

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
            <div
                className={`max-w-[70%] rounded-2xl px-4 py-3 ${isUser
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
            >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                {!isUser && message.metadata && (
                    <div className="mt-2 pt-2 border-t border-gray-300 flex gap-2 flex-wrap">
                        {message.metadata.domain && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                                {message.metadata.domain}
                            </span>
                        )}
                        {message.metadata.source && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                                {message.metadata.source}
                            </span>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}