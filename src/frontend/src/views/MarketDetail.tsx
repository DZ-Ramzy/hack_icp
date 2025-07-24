import React, { useState, useEffect } from "react";
import { BackendService } from "../services/backend";
import type {
  Market,
  AIInsight,
} from "../../../declarations/backend/backend.did";

interface MarketDetailProps {
  marketId: string;
  onBack: () => void;
}

const MarketDetail: React.FC<MarketDetailProps> = ({ marketId, onBack }) => {
  const [market, setMarket] = useState<Market | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [betAmount, setBetAmount] = useState<string>("10");
  const [selectedOutcome, setSelectedOutcome] = useState<"yes" | "no">("yes");
  const [isPlacingBet, setIsPlacingBet] = useState(false);
  const [aiInsight, setAiInsight] = useState<AIInsight | null>(null);
  const [isLoadingInsight, setIsLoadingInsight] = useState(false);
  const [showInsight, setShowInsight] = useState(false);

  useEffect(() => {
    loadMarket();
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
  }, [marketId]);

  const loadMarket = async () => {
    try {
      setLoading(true);
      const markets = await BackendService.getMarkets();
      const foundMarket = markets.find((m) => m.id.toString() === marketId);
      if (foundMarket) {
        setMarket(foundMarket);
      } else {
        setError("Market not found");
      }
    } catch (err) {
      console.error("Failed to load market:", err);
      setError("Failed to load market details");
    } finally {
      setLoading(false);
    }
  };

  const loadAIInsight = async () => {
    if (!market) return;

    try {
      setIsLoadingInsight(true);
      const insight = await BackendService.getAIInsight(market.id);
      setAiInsight(insight);
    } catch (err) {
      console.error("Failed to load AI insight:", err);
      setAiInsight(null);
    } finally {
      setIsLoadingInsight(false);
    }
  };

  const handleAIInsightClick = () => {
    if (!aiInsight && !isLoadingInsight) {
      loadAIInsight();
    }
    setShowInsight(!showInsight);
  };

  const handlePlaceBet = async () => {
    if (!market || !betAmount) return;

    try {
      setIsPlacingBet(true);
      const amount = parseFloat(betAmount);

      // Use the unified buyShares method
      await BackendService.buyShares(
        market.id,
        selectedOutcome === "yes",
        BigInt(Math.floor(amount * 100000000)), // Convert to e8s
      );

      // Reload market data to show updated shares
      await loadMarket();

      // Reset form
      setBetAmount("10");
      alert(
        `Successfully placed ${amount} ICP bet on ${selectedOutcome.toUpperCase()}!`,
      );
    } catch (err) {
      console.error("Failed to place bet:", err);
      alert("Failed to place bet. Please try again.");
    } finally {
      setIsPlacingBet(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="border-primary-purple h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"></div>
      </div>
    );
  }

  if (error || !market) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-700">
            {error || "Market not found"}
          </div>
          <button
            onClick={onBack}
            className="bg-primary-purple hover:bg-primary-purple/90 rounded-lg px-6 py-2 text-white"
          >
            Back to Markets
          </button>
        </div>
      </div>
    );
  }

  const yesLiquidity = Number(market.yes_liquidity);
  const noLiquidity = Number(market.no_liquidity);
  const totalLiquidity = yesLiquidity + noLiquidity;

  const yesPercentage =
    totalLiquidity > 0 ? Math.round((yesLiquidity / totalLiquidity) * 100) : 50;
  const noPercentage = 100 - yesPercentage;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="container mx-auto max-w-4xl px-4 py-4">
          <button
            onClick={onBack}
            className="mb-4 flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            <span>Back to Markets</span>
          </button>

          <div className="mb-2 flex items-start justify-between">
            <h1 className="flex-1 text-2xl font-bold text-gray-900">
              {market.title}
            </h1>
            <button
              onClick={handleAIInsightClick}
              disabled={isLoadingInsight}
              className="bg-primary-purple hover:bg-primary-purple/90 ml-4 flex items-center space-x-2 rounded-lg px-4 py-2 font-medium text-white transition-colors disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              <span>{isLoadingInsight ? "Loading..." : "AI Insights"}</span>
            </button>
          </div>
          <p className="mb-4 text-gray-600">{market.description}</p>

          {/* AI Insights Section */}
          {showInsight && (
            <div className="border-primary-purple/20 from-primary-purple/5 mb-6 rounded-lg border bg-gradient-to-r to-purple-100/30 p-6">
              <div className="mb-4 flex items-center space-x-2">
                <svg
                  className="text-primary-purple h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
                <h3 className="text-primary-purple text-lg font-semibold">
                  AI Market Analysis
                </h3>
              </div>

              {isLoadingInsight ? (
                <div className="flex items-center space-x-3">
                  <div className="border-primary-purple h-4 w-4 animate-spin rounded-full border-2 border-t-transparent"></div>
                  <span className="text-gray-600">
                    Analyzing market data...
                  </span>
                </div>
              ) : aiInsight ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="mb-2 font-medium text-gray-900">Summary</h4>
                    <p className="text-gray-700">{aiInsight.summary}</p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div>
                      <h4 className="mb-2 font-medium text-gray-900">
                        AI Prediction
                      </h4>
                      <div className="flex items-center space-x-2">
                        {aiInsight.prediction_lean.length > 0 ? (
                          <>
                            <span
                              className={`rounded-full px-3 py-1 text-sm font-medium ${
                                aiInsight.prediction_lean[0]
                                  ? "bg-green-100 text-green-800"
                                  : "bg-red-100 text-red-800"
                              }`}
                            >
                              {aiInsight.prediction_lean[0] ? "YES" : "NO"}
                            </span>
                            <span className="text-sm text-gray-600">
                              ({Math.round(aiInsight.confidence * 100)}%
                              confidence)
                            </span>
                          </>
                        ) : (
                          <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-800">
                            Neutral
                          </span>
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="mb-2 font-medium text-gray-900">
                        Generated
                      </h4>
                      <p className="text-sm text-gray-600">
                        {new Date(
                          Number(aiInsight.generated_at) / 1000000,
                        ).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {aiInsight.risks.length > 0 && (
                    <div>
                      <h4 className="mb-2 font-medium text-gray-900">
                        Risk Factors
                      </h4>
                      <ul className="space-y-1">
                        {aiInsight.risks.map((risk, index) => (
                          <li
                            key={index}
                            className="flex items-start space-x-2"
                          >
                            <span className="mt-1 text-orange-500">⚠️</span>
                            <span className="text-sm text-gray-700">
                              {risk}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="py-4 text-center">
                  <p className="text-gray-500">
                    No AI insights available for this market yet.
                  </p>
                  <button
                    onClick={loadAIInsight}
                    className="text-primary-purple hover:text-primary-purple/80 mt-2 font-medium"
                  >
                    Try again
                  </button>
                </div>
              )}
            </div>
          )}

          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <span>
              📊 Volume:{" "}
              {(Number(market.total_volume) / 100000000).toLocaleString(
                undefined,
                {
                  minimumFractionDigits: 0,
                  maximumFractionDigits: 2,
                },
              )}{" "}
              ICP
            </span>
            <span>
              ⏰ Ends:{" "}
              {new Date(
                Number(market.close_date) / 1000000,
              ).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      <div className="container mx-auto max-w-4xl px-4 py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Market Info */}
          <div className="space-y-6 lg:col-span-2">
            {/* Current Odds */}
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <h3 className="mb-4 text-lg font-semibold text-gray-900">
                Current Odds
              </h3>
              <div className="flex space-x-4">
                <div className="flex-1 rounded-lg border border-green-200 bg-green-50 p-4 text-center">
                  <div className="mb-1 text-sm font-medium text-green-600">
                    Yes
                  </div>
                  <div className="text-2xl font-bold text-green-700">
                    {yesPercentage}¢
                  </div>
                  <div className="text-xs text-green-600">
                    {yesPercentage}% chance
                  </div>
                </div>
                <div className="flex-1 rounded-lg border border-red-200 bg-red-50 p-4 text-center">
                  <div className="mb-1 text-sm font-medium text-red-600">
                    No
                  </div>
                  <div className="text-2xl font-bold text-red-700">
                    {noPercentage}¢
                  </div>
                  <div className="text-xs text-red-600">
                    {noPercentage}% chance
                  </div>
                </div>
              </div>
            </div>

            {/* Market Stats */}
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <h3 className="mb-4 text-lg font-semibold text-gray-900">
                Market Statistics
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Total Volume</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {(Number(market.total_volume) / 100000000).toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                      },
                    )}{" "}
                    ICP
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">24h Volume</div>
                  <div className="text-xl font-semibold text-gray-900">
                    {(Number(market.total_volume) / 100000000).toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                      },
                    )}{" "}
                    ICP
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Yes Liquidity</div>
                  <div className="text-xl font-semibold text-green-700">
                    {(Number(market.yes_liquidity) / 100000000).toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                      },
                    )}{" "}
                    ICP
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">No Liquidity</div>
                  <div className="text-xl font-semibold text-red-700">
                    {(Number(market.no_liquidity) / 100000000).toLocaleString(
                      undefined,
                      {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                      },
                    )}{" "}
                    ICP
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Betting Panel */}
          <div className="lg:col-span-1">
            <div className="sticky top-4 rounded-lg border border-gray-200 bg-white p-6">
              <h3 className="mb-4 text-lg font-semibold text-gray-900">
                Place Your Bet
              </h3>

              {/* Outcome Selection */}
              <div className="mb-4">
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Choose Outcome
                </label>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedOutcome("yes")}
                    className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
                      selectedOutcome === "yes"
                        ? "border-green-200 bg-green-50 text-green-700"
                        : "border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    Yes ({yesPercentage}¢)
                  </button>
                  <button
                    onClick={() => setSelectedOutcome("no")}
                    className={`flex-1 rounded-lg border px-4 py-2 text-sm font-medium transition-colors ${
                      selectedOutcome === "no"
                        ? "border-red-200 bg-red-50 text-red-700"
                        : "border-gray-200 bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    No ({noPercentage}¢)
                  </button>
                </div>
              </div>

              {/* Bet Amount */}
              <div className="mb-4">
                <label className="mb-2 block text-sm font-medium text-gray-700">
                  Bet Amount (ICP)
                </label>
                <input
                  type="number"
                  value={betAmount}
                  onChange={(e) => setBetAmount(e.target.value)}
                  className="focus:ring-primary-purple focus:border-primary-purple w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2"
                  placeholder="Enter amount"
                  min="0.01"
                  step="0.01"
                />
              </div>

              {/* Potential Payout */}
              <div className="mb-6 rounded-lg bg-gray-50 p-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">You pay:</span>
                  <span className="font-medium">{betAmount || "0"} ICP</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Potential payout:</span>
                  <span className="font-medium text-green-600">
                    {betAmount
                      ? (
                          parseFloat(betAmount) *
                          (selectedOutcome === "yes"
                            ? 100 / yesPercentage
                            : 100 / noPercentage)
                        ).toFixed(2)
                      : "0"}{" "}
                    ICP
                  </span>
                </div>
              </div>

              {/* Place Bet Button */}
              <button
                onClick={handlePlaceBet}
                disabled={
                  isPlacingBet || !betAmount || parseFloat(betAmount) <= 0
                }
                className={`w-full rounded-lg px-4 py-3 font-semibold text-white transition-colors ${
                  isPlacingBet || !betAmount || parseFloat(betAmount) <= 0
                    ? "cursor-not-allowed bg-gray-400"
                    : selectedOutcome === "yes"
                      ? "bg-green-600 hover:bg-green-700"
                      : "bg-red-600 hover:bg-red-700"
                }`}
              >
                {isPlacingBet
                  ? "Placing Bet..."
                  : `Bet ${betAmount || "0"} ICP on ${selectedOutcome.toUpperCase()}`}
              </button>

              <p className="mt-3 text-center text-xs text-gray-500">
                By placing a bet, you agree to our terms and conditions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketDetail;
