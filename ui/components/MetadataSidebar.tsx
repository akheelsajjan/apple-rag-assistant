import RelevanceBar from "@/components/RelevanceBar";

interface MetadataSidebarProps {
    domain?: string | null;
    source?: string | null;
    documentsUsed?: number | null;
    averageRelevanceScore?: number | null;
}

export default function MetadataSidebar({
    domain,
    source,
    documentsUsed,
    averageRelevanceScore,
}: MetadataSidebarProps) {
    const hasData = domain || source || documentsUsed !== null;

    return (
        <aside className="w-64 border-l border-gray-200 p-4 flex flex-col gap-4">
            <h2 className="text-sm font-semibold text-gray-700">Retrieval Details</h2>

            {!hasData && (
                <p className="text-sm text-gray-400">
                    Ask a question to see retrieval details here.
                </p>
            )}

            {domain && (
                <div>
                    <p className="text-xs text-gray-500 mb-1">Domain</p>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 inline-block">
                        {domain}
                    </span>
                </div>
            )}

            {source && (
                <div>
                    <p className="text-xs text-gray-500 mb-1">Source</p>
                    <span
                        className={`text-xs px-2 py-0.5 rounded-full inline-block ${source === "web"
                                ? "bg-orange-100 text-orange-700"
                                : "bg-green-100 text-green-700"
                            }`}
                    >
                        {source === "web" ? "Live web search" : "Local documents"}
                    </span>
                </div>
            )}

            {documentsUsed !== null && documentsUsed !== undefined && (
                <div>
                    <p className="text-xs text-gray-500 mb-1">Documents used</p>
                    <p className="text-sm font-medium">{documentsUsed}</p>
                </div>
            )}

            {averageRelevanceScore !== null && averageRelevanceScore !== undefined && (
                <RelevanceBar score={averageRelevanceScore} />
            )}
        </aside>
    );
}