import { useState, useEffect } from "react";
import { Loader } from "../components";
import { BackendService } from "../services/backend";
import { AuthService, type AuthState } from "../services/auth";
import type {
  Market,
  Trade,
  AIInsight,
  MarketComment,
} from "../../../declarations/backend/backend.did";

interface MarketViewProps {
  marketId: bigint;
  onBack: () => void;
}

export function MarketView({ marketId, onBack }: MarketViewProps) {
  const [market, setMarket] = useState<Market | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [aiInsight, setAIInsight] = useState<AIInsight | null>(null);
  const [comments, setComments] = useState<MarketComment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tradeAmount, setTradeAmount] = useState("");
  const [selectedSide, setSelectedSide] = useState<"yes" | "no">("yes");
  const [trading, setTrading] = useState(false);
  const [newComment, setNewComment] = useState("");
  const [addingComment, setAddingComment] = useState(false);
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    principal: null,
    identity: null,
  });

  useEffect(() => {
    loadMarketData();
    AuthService.getAuthState().then(setAuthState);
    AuthService.addAuthListener(setAuthState);

    return () => {
      AuthService.removeAuthListener(setAuthState);
    };
  }, [marketId]);

  const loadMarketData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [marketData, tradesData, insightData, commentsData] =
        await Promise.all([
          BackendService.getMarket(marketId),
          BackendService.getMarketTrades(marketId),
          BackendService.getAIInsight(marketId),
          BackendService.getMarketComments(marketId),
        ]);

      setMarket(marketData);
      setTrades(tradesData);
      setAIInsight(insightData);
      setComments(commentsData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load market data",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = async () => {
    if (!authState.isAuthenticated || !market || !tradeAmount) return;

    try {
      setTrading(true);
      const amount = BigInt(Math.floor(parseFloat(tradeAmount) * 100)); // Convert to shares

      await BackendService.buyShares(marketId, selectedSide === "yes", amount);

      // Reload market data to get updated prices
      await loadMarketData();
      setTradeAmount("");

      alert(
        `Trade successful! Bought ${amount} ${selectedSide.toUpperCase()} shares`,
      );
    } catch (err) {
      alert(
        `Trade failed: ${err instanceof Error ? err.message : "Unknown error"}`,
      );
    } finally {
      setTrading(false);
    }
  };

  const handleAddComment = async () => {
    if (!authState.isAuthenticated || !newComment.trim()) return;

    try {
      setAddingComment(true);
      await BackendService.addComment(marketId, newComment.trim());
      await loadMarketData(); // Reload to get new comments
      setNewComment("");
    } catch (err) {
      alert(
        `Failed to add comment: ${err instanceof Error ? err.message : "Unknown error"}`,
      );
    } finally {
      setAddingComment(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <Loader size="lg" />
      </div>
    );
  }

  if (error || !market) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto max-w-md rounded-lg border border-red-200 bg-red-50 p-6">
          <h3 className="mb-2 font-medium text-red-800">
            Error Loading Market
          </h3>
          <p className="mb-4 text-sm text-red-600">
            {error || "Market not found"}
          </p>
          <button
            onClick={onBack}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const yesPrice =
    Number(market.yes_shares) /
    (Number(market.yes_shares) + Number(market.no_shares));
  const noPrice = 1 - yesPrice;
  const formatPrice = (price: number) => `$${price.toFixed(3)}`;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Back Button */}
      <button
        onClick={onBack}
        className="text-primary-600 hover:text-primary-700 mb-6 flex items-center font-medium"
      >
        ← Back to Markets
      </button>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Main Content */}
        <div className="space-y-8 lg:col-span-2">
          {/* Market Header */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h1 className="mb-2 text-2xl font-bold text-gray-900">
                  {market.title}
                </h1>
                <div className="flex items-center space-x-3">
                  <span className="bg-primary-100 text-primary-700 rounded-full px-3 py-1 text-sm font-medium">
                    {market.category}
                  </span>
                  <span className="text-sm text-gray-500">
                    Closes: {BackendService.formatTimestamp(market.close_date)}
                  </span>
                </div>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-sm font-medium ${
                  BackendService.getMarketStatusText(market.status) === "Active"
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {BackendService.getMarketStatusText(market.status)}
              </span>
            </div>

            <p className="leading-relaxed text-gray-600">
              {market.description}
            </p>

            <div className="mt-6 grid grid-cols-3 gap-6 border-t border-gray-100 pt-6">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  ${Number(market.total_volume).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Volume</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {Number(
                    market.yes_shares + market.no_shares,
                  ).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">Total Shares</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {trades.length}
                </div>
                <div className="text-sm text-gray-600">Total Trades</div>
              </div>
            </div>
          </div>

          {/* Price Chart */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">
              Price Evolution
            </h2>

            {/* Simple price bars for now - in a real app you'd use a proper chart library */}
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <div className="mb-2 text-3xl font-bold text-green-600">
                  {formatPrice(yesPrice)}
                </div>
                <div className="mb-4 font-medium text-green-700">YES</div>
                <div className="flex h-32 items-end rounded-lg bg-green-100">
                  <div
                    className="w-full rounded-b-lg bg-green-500 transition-all duration-500"
                    style={{ height: `${yesPrice * 100}%` }}
                  ></div>
                </div>
              </div>

              <div className="text-center">
                <div className="mb-2 text-3xl font-bold text-red-600">
                  {formatPrice(noPrice)}
                </div>
                <div className="mb-4 font-medium text-red-700">NO</div>
                <div className="flex h-32 items-end rounded-lg bg-red-100">
                  <div
                    className="w-full rounded-b-lg bg-red-500 transition-all duration-500"
                    style={{ height: `${noPrice * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Insight */}
          {aiInsight && (
            <div className="rounded-xl border border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50 p-6">
              <div className="mb-4 flex items-center space-x-2">
                <div className="h-3 w-3 animate-pulse rounded-full bg-purple-500"></div>
                <h2 className="text-xl font-semibold text-purple-900">
                  AI Insight
                </h2>
                <span className="text-sm text-purple-600">
                  Confidence: {Math.round(aiInsight.confidence * 100)}%
                </span>
              </div>

              <p className="mb-4 text-purple-800">{aiInsight.summary}</p>

              {aiInsight.prediction_lean.length > 0 && (
                <div className="mb-4">
                  <span className="font-medium text-purple-700">
                    AI Prediction:{" "}
                  </span>
                  <span
                    className={`font-bold ${
                      aiInsight.prediction_lean[0]
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {aiInsight.prediction_lean[0] ? "YES" : "NO"}
                  </span>
                </div>
              )}

              {aiInsight.risks.length > 0 && (
                <div>
                  <div className="mb-2 font-medium text-purple-700">
                    Key Risks:
                  </div>
                  <ul className="space-y-1 text-sm text-purple-600">
                    {aiInsight.risks.map((risk, index) => (
                      <li key={index}>• {risk}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Comments Section */}
          <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">
              Discussion
            </h2>

            {/* Add Comment */}
            {authState.isAuthenticated && (
              <div className="mb-6">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Share your thoughts..."
                  className="focus:ring-primary-500 w-full resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
                  rows={3}
                  maxLength={500}
                />
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    {500 - newComment.length} characters remaining
                  </span>
                  <button
                    onClick={handleAddComment}
                    disabled={!newComment.trim() || addingComment}
                    className="bg-primary-600 hover:bg-primary-700 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors disabled:bg-gray-300"
                  >
                    {addingComment ? "Posting..." : "Post Comment"}
                  </button>
                </div>
              </div>
            )}

            {/* Comments List */}
            <div className="space-y-4">
              {comments.length === 0 ? (
                <p className="py-8 text-center text-gray-500">
                  No comments yet. Be the first to share your thoughts!
                </p>
              ) : (
                comments.map((comment) => (
                  <div
                    key={comment.id.toString()}
                    className="border-b border-gray-100 pb-4 last:border-b-0"
                  >
                    <div className="mb-2 flex items-start justify-between">
                      <span className="font-medium text-gray-900">
                        {comment.author.toString().slice(0, 8)}...
                        {comment.author.toString().slice(-4)}
                      </span>
                      <span className="text-sm text-gray-500">
                        {BackendService.formatTimestamp(comment.timestamp)}
                      </span>
                    </div>
                    <p className="text-gray-700">{comment.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Trading Sidebar */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-6 text-xl font-semibold text-gray-900">
              Trade Shares
            </h2>

            {authState.isAuthenticated ? (
              <div className="space-y-6">
                {/* Side Selection */}
                <div>
                  <label className="mb-3 block text-sm font-medium text-gray-700">
                    Choose Side
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={() => setSelectedSide("yes")}
                      className={`rounded-lg border-2 p-4 transition-colors ${
                        selectedSide === "yes"
                          ? "border-green-500 bg-green-50 text-green-700"
                          : "border-gray-200 hover:border-green-300"
                      }`}
                    >
                      <div className="text-lg font-bold">
                        {formatPrice(yesPrice)}
                      </div>
                      <div className="text-sm">YES</div>
                    </button>
                    <button
                      onClick={() => setSelectedSide("no")}
                      className={`rounded-lg border-2 p-4 transition-colors ${
                        selectedSide === "no"
                          ? "border-red-500 bg-red-50 text-red-700"
                          : "border-gray-200 hover:border-red-300"
                      }`}
                    >
                      <div className="text-lg font-bold">
                        {formatPrice(noPrice)}
                      </div>
                      <div className="text-sm">NO</div>
                    </button>
                  </div>
                </div>

                {/* Amount Input */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">
                    Amount ($)
                  </label>
                  <input
                    type="number"
                    value={tradeAmount}
                    onChange={(e) => setTradeAmount(e.target.value)}
                    placeholder="Enter amount"
                    min="0.01"
                    step="0.01"
                    className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
                  />
                </div>

                {/* Trade Button */}
                <button
                  onClick={handleTrade}
                  disabled={
                    !tradeAmount ||
                    trading ||
                    BackendService.getMarketStatusText(market.status) !==
                      "Active"
                  }
                  className={`w-full rounded-lg py-3 font-medium transition-colors ${
                    selectedSide === "yes"
                      ? "bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-300"
                      : "bg-red-600 text-white hover:bg-red-700 disabled:bg-gray-300"
                  }`}
                >
                  {trading
                    ? "Processing..."
                    : `Buy ${selectedSide.toUpperCase()} Shares`}
                </button>

                {BackendService.getMarketStatusText(market.status) !==
                  "Active" && (
                  <p className="text-center text-sm text-gray-500">
                    Market is{" "}
                    {BackendService.getMarketStatusText(
                      market.status,
                    ).toLowerCase()}
                  </p>
                )}
              </div>
            ) : (
              <div className="text-center">
                <p className="mb-4 text-gray-600">
                  Connect your wallet to start trading
                </p>
                <button
                  onClick={() => AuthService.login()}
                  className="bg-primary-600 hover:bg-primary-700 w-full rounded-lg py-3 font-medium text-white transition-colors"
                >
                  Connect Wallet
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
