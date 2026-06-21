interface RelevanceBarProps {
    score: number;
}

export default function RelevanceBar({ score }: RelevanceBarProps) {
    const percentage = Math.round(score * 100);

    const colorClass =
        score >= 0.7 ? "bg-green-500" : score >= 0.4 ? "bg-yellow-500" : "bg-red-500";

    return (
        <div>
            <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Relevance</span>
                <span>{percentage}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                    className={`h-full ${colorClass} transition-all duration-300`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}