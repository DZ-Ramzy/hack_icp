import { type Market } from "../../../declarations/backend/backend.did";
import { BackendService } from "../services/backend";

interface MarketCardProps {
  market: Market;
  onSelect: (marketId: bigint) => void;
  showAIInsight?: boolean;
}

export function MarketCard({
  market,
  onSelect,
  showAIInsight = true,
}: MarketCardProps) {
  const yesPrice =
    Number(market.yes_shares) /
    (Number(market.yes_shares) + Number(market.no_shares));
  const noPrice = 1 - yesPrice;

  const formatPrice = (price: number) => `$${price.toFixed(3)}`;
  const formatVolume = (volume: bigint) =>
    `$${Number(volume).toLocaleString()}`;

  const statusColor = {
    Active: "bg-green-100 text-green-800",
    Closed: "bg-yellow-100 text-yellow-800",
    Resolved: "bg-blue-100 text-blue-800",
    Pending: "bg-gray-100 text-gray-800",
  };

  const status = BackendService.getMarketStatusText(market.status);

  return (
    <div
      className="prediction-card cursor-pointer rounded-xl p-6 transition-all duration-200 hover:shadow-lg"
      onClick={() => onSelect(market.id)}
    >
      {/* Header */}
      <div className="mb-4 flex items-start justify-between">
        <div className="flex-1">
          <h3 className="mb-2 line-clamp-2 text-lg font-semibold text-gray-900">
            {market.title}
          </h3>
          <div className="flex items-center space-x-3 text-sm text-gray-600">
            <span className="bg-primary-100 text-primary-700 rounded-full px-2 py-1 text-xs font-medium">
              {market.category}
            </span>
            <span
              className={`rounded-full px-2 py-1 text-xs font-medium ${statusColor[status as keyof typeof statusColor]}`}
            >
              {status}
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="mb-4 line-clamp-2 text-sm text-gray-600">
        {market.description}
      </p>

      {/* Price Display */}
      <div className="mb-4 grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-green-200 bg-green-50 p-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-green-700">YES</span>
            <span className="font-bold text-green-900">
              {formatPrice(yesPrice)}
            </span>
          </div>
          <div className="mt-1 text-xs text-green-600">
            {Number(market.yes_shares).toLocaleString()} shares
          </div>
        </div>

        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-red-700">NO</span>
            <span className="font-bold text-red-900">
              {formatPrice(noPrice)}
            </span>
          </div>
          <div className="mt-1 text-xs text-red-600">
            {Number(market.no_shares).toLocaleString()} shares
          </div>
        </div>
      </div>

      {/* AI Insight Preview */}
      {showAIInsight && (
        <div className="mb-4 rounded-lg border border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50 p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 animate-pulse rounded-full bg-purple-500"></div>
              <span className="text-sm font-medium text-purple-700">
                AI Insight
              </span>
            </div>
            <span className="text-xs text-purple-600">Click to view</span>
          </div>
        </div>
      )}

      {/* Footer Stats */}
      <div className="flex items-center justify-between border-t border-gray-100 pt-3 text-sm text-gray-500">
        <span>Volume: {formatVolume(market.total_volume)}</span>
        <span>Closes: {BackendService.formatTimestamp(market.close_date)}</span>
      </div>
    </div>
  );
}
