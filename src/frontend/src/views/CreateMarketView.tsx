import { useState, useEffect } from "react";
import { Loader } from "../components";
import { BackendService } from "../services/backend";
import { AuthService, type AuthState } from "../services/auth";

interface CreateMarketViewProps {
  onMarketCreated: (marketId: bigint) => void;
}

export function CreateMarketView({ onMarketCreated }: CreateMarketViewProps) {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    principal: null,
    identity: null,
  });
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [closeDate, setCloseDate] = useState("");
  const [customCategory, setCustomCategory] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predefinedCategories = [
    "Cryptocurrency",
    "Technology",
    "Finance",
    "Politics",
    "Sports",
    "Entertainment",
    "Science",
    "Climate",
    "Custom",
  ];

  useEffect(() => {
    AuthService.getAuthState().then(setAuthState);
    AuthService.addAuthListener(setAuthState);

    return () => {
      AuthService.removeAuthListener(setAuthState);
    };
  }, []);

  const validateForm = () => {
    if (!title.trim()) {
      setError("Title is required");
      return false;
    }
    if (title.length < 10) {
      setError("Title must be at least 10 characters");
      return false;
    }
    if (!description.trim()) {
      setError("Description is required");
      return false;
    }
    if (description.length < 50) {
      setError("Description must be at least 50 characters");
      return false;
    }
    if (!category || (category === "Custom" && !customCategory.trim())) {
      setError("Category is required");
      return false;
    }
    if (!closeDate) {
      setError("Close date is required");
      return false;
    }

    const selectedDate = new Date(closeDate);
    const now = new Date();
    if (selectedDate <= now) {
      setError("Close date must be in the future");
      return false;
    }

    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 2);
    if (selectedDate > maxDate) {
      setError("Close date cannot be more than 2 years in the future");
      return false;
    }

    setError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!authState.isAuthenticated) {
      setError("Please connect your wallet first");
      return;
    }

    if (!validateForm()) return;

    try {
      setCreating(true);
      setError(null);

      const selectedCategory =
        category === "Custom" ? customCategory.trim() : category;
      const closeDateTimestamp = BigInt(
        new Date(closeDate).getTime() * 1000000,
      ); // Convert to nanoseconds

      const marketId = await BackendService.createMarket(
        title.trim(),
        description.trim(),
        selectedCategory,
        closeDateTimestamp,
      );

      // Reset form
      setTitle("");
      setDescription("");
      setCategory("");
      setCustomCategory("");
      setCloseDate("");

      alert("Market created successfully! It's now pending validation.");
      onMarketCreated(marketId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create market");
    } finally {
      setCreating(false);
    }
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split("T")[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() + 2);
    return maxDate.toISOString().split("T")[0];
  };

  if (!authState.isAuthenticated) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 text-center">
        <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
          <h1 className="mb-4 text-3xl font-bold text-gray-900">
            Create a Market
          </h1>
          <p className="mb-8 text-gray-600">
            Connect your wallet to create prediction markets and start earning
            rewards.
          </p>
          <button
            onClick={() => AuthService.login()}
            className="bg-primary-600 hover:bg-primary-700 rounded-lg px-8 py-3 font-medium text-white transition-colors"
          >
            Connect Wallet
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="mb-4 text-3xl font-bold text-gray-900">
          Create a New Market
        </h1>
        <p className="text-gray-600">
          Create a prediction market for others to trade on. Markets require
          validation before becoming active.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Form */}
        <div className="lg:col-span-2">
          <form
            onSubmit={handleSubmit}
            className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
          >
            {/* Title */}
            <div>
              <label
                htmlFor="title"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Market Title *
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Will Bitcoin reach $150,000 by end of 2025?"
                className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
                maxLength={200}
              />
              <div className="mt-1 text-right text-sm text-gray-500">
                {title.length}/200 characters
              </div>
            </div>

            {/* Description */}
            <div>
              <label
                htmlFor="description"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Description *
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="This market resolves to YES if Bitcoin (BTC) reaches or exceeds $150,000 USD by December 31, 2025. The resolution will be based on the highest price recorded on major exchanges..."
                className="focus:ring-primary-500 w-full resize-none rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
                rows={6}
                maxLength={1000}
              />
              <div className="mt-1 text-right text-sm text-gray-500">
                {description.length}/1000 characters
              </div>
            </div>

            {/* Category */}
            <div>
              <label
                htmlFor="category"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Category *
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
              >
                <option value="">Select a category</option>
                {predefinedCategories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>

              {category === "Custom" && (
                <input
                  type="text"
                  value={customCategory}
                  onChange={(e) => setCustomCategory(e.target.value)}
                  placeholder="Enter custom category"
                  className="focus:ring-primary-500 mt-3 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
                  maxLength={50}
                />
              )}
            </div>

            {/* Close Date */}
            <div>
              <label
                htmlFor="closeDate"
                className="mb-2 block text-sm font-medium text-gray-700"
              >
                Market Close Date *
              </label>
              <input
                type="date"
                id="closeDate"
                value={closeDate}
                onChange={(e) => setCloseDate(e.target.value)}
                min={getMinDate()}
                max={getMaxDate()}
                className="focus:ring-primary-500 w-full rounded-lg border border-gray-300 px-4 py-3 focus:border-transparent focus:ring-2"
              />
              <p className="mt-1 text-sm text-gray-500">
                Markets close on the specified date and cannot accept new trades
                after that.
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={creating}
              className="flex w-full items-center justify-center rounded-lg bg-purple-600 py-3 font-medium text-white transition-colors hover:bg-purple-700 disabled:bg-gray-300"
            >
              {creating ? (
                <>
                  <Loader size="sm" className="mr-2" />
                  Creating Market...
                </>
              ) : (
                "Create Market"
              )}
            </button>
          </form>
        </div>

        {/* Guidelines */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-gray-900">
              Market Guidelines
            </h3>

            <div className="space-y-4 text-sm text-gray-600">
              <div>
                <h4 className="mb-1 font-medium text-gray-900">Clear Title</h4>
                <p>
                  Make your title specific and unambiguous. Include timeframes
                  and precise conditions.
                </p>
              </div>

              <div>
                <h4 className="mb-1 font-medium text-gray-900">
                  Detailed Description
                </h4>
                <p>
                  Explain exactly how the market will resolve. Include sources
                  and edge cases.
                </p>
              </div>

              <div>
                <h4 className="mb-1 font-medium text-gray-900">
                  Fair Resolution
                </h4>
                <p>
                  Ensure the outcome can be objectively determined using
                  reliable sources.
                </p>
              </div>

              <div>
                <h4 className="mb-1 font-medium text-gray-900">
                  Validation Process
                </h4>
                <p>
                  All markets undergo AI review and admin validation before
                  becoming active.
                </p>
              </div>
            </div>

            <div className="mt-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4">
              <div className="flex items-start">
                <div className="mr-2 text-yellow-600">⚠️</div>
                <div>
                  <h4 className="mb-1 text-sm font-medium text-yellow-800">
                    Important
                  </h4>
                  <p className="text-sm text-yellow-700">
                    Markets require validation before trading begins. This
                    process may take 24-48 hours.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
