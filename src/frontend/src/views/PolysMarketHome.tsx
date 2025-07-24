import React, { useState, useEffect } from "react";
import { BackendService } from "../services/backend";
import type { Market } from "../../../declarations/backend/backend.did";
import MarketDetail from "./MarketDetail";

interface PolysMarketHomeProps {
  onNavigate?: (page: string) => void;
}

const PolysMarketHome: React.FC<PolysMarketHomeProps> = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"all" | "trending" | "new">("all");
  const [selectedMarketId, setSelectedMarketId] = useState<string | null>(null);

  useEffect(() => {
    loadMarkets();
  }, []);

  const loadMarkets = async () => {
    try {
      setLoading(true);
      const fetchedMarkets = await BackendService.getMarkets();
      setMarkets(fetchedMarkets);
      setError(null);
    } catch (err) {
      console.error("Failed to load markets:", err);
      setError("Failed to load markets. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToHowItWorks = () => {
    const element = document.getElementById("how-it-works");
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleMarketClick = (marketId: string) => {
    // Smooth scroll to top before navigation
    window.scrollTo({ top: 0, behavior: "smooth" });
    // Small delay to let the scroll animation start
    setTimeout(() => {
      setSelectedMarketId(marketId);
    }, 100);
  };

  const scrollToMarkets = () => {
    const element = document.getElementById("markets-section");
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  // If a market is selected, show the market detail page
  if (selectedMarketId) {
    return (
      <MarketDetail
        marketId={selectedMarketId}
        onBack={() => {
          setSelectedMarketId(null);
          // Scroll to top when returning to markets list
          setTimeout(() => window.scrollTo(0, 0), 100);
        }}
      />
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <div className="border-primary-purple h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto max-w-4xl px-4 py-16 text-center">
        <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-700">
          {error}
        </div>
        <button
          onClick={loadMarkets}
          className="bg-primary-purple hover:bg-primary-purple/90 rounded-lg px-6 py-2 text-white"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section - Modern Web3 Design */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Animated Background Pattern */}
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%235b2c87' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='1.5'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        ></div>

        {/* Gradient Overlay */}
        <div className="from-primary-purple/20 absolute inset-0 bg-gradient-to-t via-transparent to-transparent"></div>

        <div className="container relative mx-auto max-w-7xl px-4 py-20 sm:py-28 lg:py-32">
          <div className="text-center">
            {/* Main Headline with Animation */}
            <div className="animate-fade-in">
              <h1 className="text-4xl font-bold text-white sm:text-5xl lg:text-7xl xl:text-8xl">
                <span className="block">Predict the future.</span>
                <span className="from-primary-purple mt-2 block bg-gradient-to-r to-cyan-400 bg-clip-text text-transparent">
                  Powered by AI.
                </span>
                <span className="mt-2 block text-slate-200">
                  Secured by ICP.
                </span>
              </h1>
            </div>

            {/* Subheadline */}
            <div className="animate-slide-up mt-8">
              <p className="mx-auto max-w-4xl text-lg leading-relaxed text-slate-300 sm:text-xl lg:text-2xl">
                Discover{" "}
                <span className="font-semibold text-white">
                  ChainPredict ICP
                </span>{" "}
                — the decentralized prediction market where AI creates markets
                and insights, and users trade trustlessly.
                <span className="mt-2 block font-medium text-cyan-200">
                  No oracles. No middlemen. Just real, on-chain forecasting.
                </span>
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="animate-fade-in mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
              <button
                onClick={scrollToMarkets}
                className="bg-primary-purple hover:shadow-primary-purple/25 group relative overflow-hidden rounded-xl px-8 py-4 text-lg font-semibold text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl sm:px-10 sm:py-5"
                aria-label="Explore prediction markets"
              >
                <span className="relative z-10">Explore Markets</span>
                <div className="from-primary-purple absolute inset-0 bg-gradient-to-r to-purple-600 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
              </button>

              <button
                onClick={scrollToHowItWorks}
                className="group rounded-xl border-2 border-slate-400 px-8 py-4 text-lg font-semibold text-slate-200 transition-all duration-300 hover:border-white hover:bg-white/10 hover:text-white sm:px-10 sm:py-5"
                aria-label="Learn how ChainPredict ICP works"
              >
                <span className="flex items-center space-x-2">
                  <span>How it Works</span>
                  <svg
                    className="h-5 w-5 transition-transform group-hover:translate-x-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </span>
              </button>
            </div>

            {/* Floating Elements for Visual Appeal */}
            <div className="animate-float absolute left-10 top-20 h-20 w-20 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 opacity-20 blur-xl"></div>
            <div
              className="animate-float absolute right-10 top-32 h-16 w-16 rounded-full bg-gradient-to-r from-purple-400 to-pink-500 opacity-20 blur-xl"
              style={{ animationDelay: "2s" }}
            ></div>
            <div
              className="animate-float absolute bottom-20 left-1/4 h-12 w-12 rounded-full bg-gradient-to-r from-emerald-400 to-cyan-500 opacity-20 blur-xl"
              style={{ animationDelay: "4s" }}
            ></div>
          </div>
        </div>

        {/* Bottom Fade */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gray-50 to-transparent"></div>
        <br />
        <br />
        <br />
        <br />
      </section>

      {/* Navigation Tabs */}
      <section className="sticky top-16 z-40 border-b border-gray-200 bg-white">
        <div className="container mx-auto max-w-6xl px-4">
          <div className="flex space-x-8">
            {[
              { id: "all", label: "All Markets", count: markets.length },
              { id: "trending", label: "Trending", count: 0 },
              { id: "new", label: "New", count: 0 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`border-b-2 px-2 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? "border-primary-purple text-primary-purple"
                    : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                }`}
              >
                {tab.label}
                {tab.count > 0 && (
                  <span className="ml-2 rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-600">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Markets Grid */}
      <section id="markets-section" className="py-8">
        <div className="container mx-auto max-w-6xl px-4">
          {markets.length === 0 ? (
            <div className="py-16 text-center">
              <div className="mb-4 text-6xl">📊</div>
              <h3 className="mb-2 text-xl font-semibold text-gray-900">
                No markets yet
              </h3>
              <p className="mb-6 text-gray-600">
                Be the first to create a prediction market!
              </p>
              <button className="bg-primary-purple hover:bg-primary-purple/90 rounded-lg px-6 py-2 font-semibold text-white">
                Create Market
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {markets.map((market) => (
                <div
                  key={market.id.toString()}
                  onClick={() => handleMarketClick(market.id.toString())}
                  className="hover:shadow-primary-purple/10 hover:border-primary-purple/30 group cursor-pointer rounded-lg border border-gray-200 bg-white p-6 transition-all hover:shadow-lg"
                >
                  <div className="mb-4 flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="group-hover:text-primary-purple mb-2 text-lg font-medium text-gray-900 transition-colors">
                        {market.title}
                      </h3>
                      <p className="mb-3 text-sm text-gray-600">
                        {market.description}
                      </p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span>
                          📊 Volume:{" "}
                          {(
                            Number(market.total_volume) / 100000000
                          ).toLocaleString(undefined, {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 2,
                          })}{" "}
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
                    <div className="ml-4">
                      <svg
                        className="group-hover:text-primary-purple h-5 w-5 text-gray-400 transition-colors"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex space-x-3">
                      <div className="min-w-[100px] rounded-lg border border-green-200 bg-green-50 px-4 py-2 text-center">
                        <div className="text-sm font-medium text-green-600">
                          Yes
                        </div>
                        <div className="text-lg font-bold text-green-700">
                          {(() => {
                            const yesLiq = Number(market.yes_liquidity);
                            const noLiq = Number(market.no_liquidity);
                            const total = yesLiq + noLiq;
                            if (total === 0) return "50¢";
                            const percentage = Math.round(
                              (yesLiq / total) * 100,
                            );
                            return `${percentage}¢`;
                          })()}
                        </div>
                      </div>
                      <div className="min-w-[100px] rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-center">
                        <div className="text-sm font-medium text-red-600">
                          No
                        </div>
                        <div className="text-lg font-bold text-red-700">
                          {(() => {
                            const yesLiq = Number(market.yes_liquidity);
                            const noLiq = Number(market.no_liquidity);
                            const total = yesLiq + noLiq;
                            if (total === 0) return "50¢";
                            const percentage = Math.round(
                              (noLiq / total) * 100,
                            );
                            return `${percentage}¢`;
                          })()}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-sm text-gray-500">24h Volume</div>
                      <div className="font-semibold text-gray-900">
                        {(
                          Number(market.total_volume) / 100000000
                        ).toLocaleString(undefined, {
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 2,
                        })}{" "}
                        ICP
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* How it Works Section */}
      <section
        id="how-it-works"
        className="border-t border-gray-200 bg-white py-16"
      >
        <div className="container mx-auto max-w-6xl px-4">
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-gray-900">
              How ChainPredict ICP Works
            </h2>
            <p className="text-lg text-gray-600">
              AI-powered prediction markets on the Internet Computer
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="text-center">
              <div className="bg-primary-purple mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full text-white">
                <svg
                  className="h-8 w-8"
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
              </div>
              <h3 className="mb-2 text-xl font-semibold text-gray-900">
                Anyone Can Create Markets
              </h3>
              <p className="text-gray-600">
                Users can freely create prediction markets about crypto, sports,
                politics, and more. No central authority neede
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-purple mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full text-white">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-gray-900">
                Trade Trustlessly
              </h3>
              <p className="text-gray-600">
                Buy YES or NO shares through an AMM system directly on-chain —
                fully decentralized, without middlemen.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-primary-purple mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full text-white">
                <svg
                  className="h-8 w-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-gray-900">
                Earn Rewards
              </h3>
              <p className="text-gray-600">
                Successful predictions are rewarded with ICP tokens
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PolysMarketHome;
