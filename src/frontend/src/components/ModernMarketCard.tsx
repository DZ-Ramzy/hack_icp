import { useState } from "react";

interface MarketCardProps {
  id: bigint;
  title: string;
  description: string;
  category: string;
  yesShares: bigint;
  noShares: bigint;
  totalVolume: bigint;
  closeDate: bigint;
  status: string;
  onSelect: (id: bigint) => void;
}

export function ModernMarketCard({
  id,
  title,
  description,
  category,
  yesShares,
  noShares,
  totalVolume,
  closeDate,
  status,
  onSelect,
}: MarketCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const totalShares = Number(yesShares) + Number(noShares);
  const yesPercentage =
    totalShares > 0 ? (Number(yesShares) / totalShares) * 100 : 50;
  const noPercentage = 100 - yesPercentage;

  const formatDate = (timestamp: bigint) => {
    const date = new Date(Number(timestamp) * 1000);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatVolume = (volume: bigint) => {
    const num = Number(volume);
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      Technology: "💻",
      Cryptocurrency: "₿",
      Finance: "💰",
      Sports: "⚽",
      Politics: "🗳️",
      Entertainment: "🎬",
      Science: "🔬",
      default: "📊",
    };
    return icons[category] || icons.default;
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      Technology: "bg-gradient-primary",
      Cryptocurrency: "bg-gradient-secondary",
      Finance: "bg-gradient-accent",
      Sports: "bg-gradient-primary",
      Politics: "bg-gradient-secondary",
      Entertainment: "bg-gradient-accent",
      Science: "bg-gradient-primary",
      default: "bg-gradient-primary",
    };
    return colors[category] || colors.default;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "bg-green-100 text-green-800";
      case "closed":
        return "bg-yellow-100 text-yellow-800";
      case "resolved":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div
      className={`card-gradient hover-lift hover-glow group relative cursor-pointer overflow-hidden transition-all duration-300 ${
        isHovered ? "scale-105" : ""
      }`}
      onClick={() => onSelect(id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div
            className={`h-10 w-10 rounded-xl bg-gradient-to-r ${getCategoryColor(category)} flex items-center justify-center shadow-lg`}
          >
            <span className="text-lg">{getCategoryIcon(category)}</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-600">
                {category}
              </span>
              <span
                className={`rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(status)}`}
              >
                {status}
              </span>
            </div>
            <div className="mt-1 text-xs text-gray-500">
              Closes {formatDate(closeDate)}
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="text-xs text-gray-500">Volume</div>
          <div className="text-sm font-bold text-gray-900">
            ${formatVolume(totalVolume)}
          </div>
        </div>
      </div>

      {/* Title and Description */}
      <div className="mb-6">
        <h3 className="group-hover:text-primary-700 mb-2 line-clamp-2 text-lg font-semibold text-gray-900 transition-colors">
          {title}
        </h3>
        <p className="line-clamp-2 text-sm text-gray-600">{description}</p>
      </div>

      {/* Prediction Bars */}
      <div className="mb-6 space-y-4">
        {/* Yes Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 rounded-full bg-gradient-to-r from-green-400 to-green-500"></div>
              <span className="text-sm font-medium text-gray-700">YES</span>
            </div>
            <span className="text-sm font-bold text-green-600">
              {yesPercentage.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-gradient-to-r from-green-400 to-green-500 transition-all duration-500 ease-out"
              style={{ width: `${yesPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* No Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 rounded-full bg-gradient-to-r from-red-400 to-red-500"></div>
              <span className="text-sm font-medium text-gray-700">NO</span>
            </div>
            <span className="text-sm font-bold text-red-600">
              {noPercentage.toFixed(1)}%
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-gradient-to-r from-red-400 to-red-500 transition-all duration-500 ease-out"
              style={{ width: `${noPercentage}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <button className="btn-primary w-full transition-all duration-200 group-hover:scale-105 group-hover:shadow-xl">
        <span className="flex items-center justify-center space-x-2">
          <span>Trade Now</span>
          <svg
            className="h-4 w-4 transition-transform group-hover:translate-x-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </span>
      </button>

      {/* Hover Overlay Effect */}
      <div
        className={`from-primary-500/5 to-primary-600/5 pointer-events-none absolute inset-0 rounded-xl bg-gradient-to-r opacity-0 transition-opacity duration-300 group-hover:opacity-100`}
      ></div>
    </div>
  );
}
