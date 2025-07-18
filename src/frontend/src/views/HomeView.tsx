import { useState, useEffect } from "react";
import { MarketCard, Loader } from "../components";
import { BackendService, type MarketFilters } from "../services/backend";
import type { Market } from "../../../declarations/backend/backend.did";

interface HomeViewProps {
  onMarketSelect: (marketId: bigint) => void;
}

export function HomeView({ onMarketSelect }: HomeViewProps) {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [filteredMarkets, setFilteredMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<MarketFilters>({});
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadMarkets();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [markets, filters, searchTerm]);

  const loadMarkets = async () => {
    try {
      setLoading(true);
      setError(null);
      const marketData = await BackendService.getMarkets();
      setMarkets(marketData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load markets");
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = BackendService.filterMarkets(markets, filters);

    if (searchTerm) {
      filtered = filtered.filter(
        (market) =>
          market.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          market.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          market.category.toLowerCase().includes(searchTerm.toLowerCase()),
      );
    }

    setFilteredMarkets(filtered);
  };

  const handleFilterChange = (newFilters: Partial<MarketFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm("");
  };

  const categories = Array.from(new Set(markets.map((m) => m.category)));

  if (loading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <Loader size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto max-w-md rounded-lg border border-red-200 bg-red-50 p-6">
          <h3 className="mb-2 font-medium text-red-800">
            Error Loading Markets
          </h3>
          <p className="mb-4 text-sm text-red-600">{error}</p>
          <button
            onClick={loadMarkets}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold text-gray-900">
          Decentralized Prediction Markets
        </h1>
        <p className="mx-auto max-w-3xl text-xl text-gray-600">
          Trade on future events with AI-powered insights. Create markets, make
          predictions, and earn rewards on the Internet Computer.
        </p>
      </div>

      {/* Filters and Search */}
      <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search markets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-transparent focus:ring-2"
            />
          </div>

          {/* Status Filter */}
          <select
            value={filters.status || ""}
            onChange={(e) =>
              handleFilterChange({
                status: (e.target.value as any) || undefined,
              })
            }
            className="focus:ring-primary-500 rounded-lg border border-gray-300 px-4 py-2 focus:border-transparent focus:ring-2"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
            <option value="resolved">Resolved</option>
            <option value="pending">Pending</option>
          </select>

          {/* Category Filter */}
          <select
            value={filters.category || ""}
            onChange={(e) =>
              handleFilterChange({ category: e.target.value || undefined })
            }
            className="focus:ring-primary-500 rounded-lg border border-gray-300 px-4 py-2 focus:border-transparent focus:ring-2"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>

          {/* Clear Filters */}
          {(filters.status || filters.category || searchTerm) && (
            <button
              onClick={clearFilters}
              className="rounded-lg border border-gray-300 px-4 py-2 text-gray-600 hover:bg-gray-50 hover:text-gray-800"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Market Stats */}
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-gray-900">
            {markets.length}
          </div>
          <div className="text-gray-600">Total Markets</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-green-600">
            {
              markets.filter(
                (m) =>
                  BackendService.getMarketStatusText(m.status) === "Active",
              ).length
            }
          </div>
          <div className="text-gray-600">Active Markets</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-blue-600">
            $
            {markets
              .reduce((sum, m) => sum + Number(m.total_volume), 0)
              .toLocaleString()}
          </div>
          <div className="text-gray-600">Total Volume</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="text-2xl font-bold text-purple-600">
            {categories.length}
          </div>
          <div className="text-gray-600">Categories</div>
        </div>
      </div>

      {/* Markets Grid */}
      {filteredMarkets.length === 0 ? (
        <div className="py-12 text-center">
          <div className="mb-4 text-lg text-gray-500">
            {searchTerm || filters.status || filters.category
              ? "No markets match your filters"
              : "No markets available"}
          </div>
          {(searchTerm || filters.status || filters.category) && (
            <button
              onClick={clearFilters}
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredMarkets.map((market) => (
            <MarketCard
              key={market.id.toString()}
              market={market}
              onSelect={onMarketSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}
