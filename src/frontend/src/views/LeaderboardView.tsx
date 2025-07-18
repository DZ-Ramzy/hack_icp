import { useState, useEffect } from "react";
import { Loader } from "../components";
import { BackendService } from "../services/backend";
import type { UserProfile } from "../../../declarations/backend/backend.did";

export function LeaderboardView() {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const leaderboardData = await BackendService.getLeaderboard();
      setUsers(leaderboardData);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load leaderboard",
      );
    } finally {
      setLoading(false);
    }
  };

  const formatPrincipal = (principal: string) => {
    return `${principal.slice(0, 8)}...${principal.slice(-4)}`;
  };

  const getAccuracyPercentage = (user: UserProfile) => {
    if (user.total_trades === 0n) return 0;
    return Math.round(
      (Number(user.successful_predictions) / Number(user.total_trades)) * 100,
    );
  };

  const getRankBadge = (rank: number) => {
    switch (rank) {
      case 1:
        return "🥇";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return `#${rank}`;
    }
  };

  const getXPLevel = (xp: bigint) => {
    const xpNum = Number(xp);
    if (xpNum < 100) return { level: 1, title: "Novice" };
    if (xpNum < 500) return { level: 2, title: "Trader" };
    if (xpNum < 1000) return { level: 3, title: "Analyst" };
    if (xpNum < 2500) return { level: 4, title: "Expert" };
    if (xpNum < 5000) return { level: 5, title: "Master" };
    return { level: 6, title: "Legend" };
  };

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
            Error Loading Leaderboard
          </h3>
          <p className="mb-4 text-sm text-red-600">{error}</p>
          <button
            onClick={loadLeaderboard}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="mb-4 text-4xl font-bold text-gray-900">Leaderboard</h1>
        <p className="text-xl text-gray-600">
          Top traders ranked by experience points, accuracy, and trading volume
        </p>
      </div>

      {/* Stats Overview */}
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm">
          <div className="text-primary-600 mb-2 text-2xl font-bold">
            {users.length}
          </div>
          <div className="text-gray-600">Active Traders</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm">
          <div className="mb-2 text-2xl font-bold text-green-600">
            {users
              .reduce((sum, user) => sum + Number(user.total_trades), 0)
              .toLocaleString()}
          </div>
          <div className="text-gray-600">Total Trades</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm">
          <div className="mb-2 text-2xl font-bold text-blue-600">
            {users.length > 0
              ? Math.round(
                  users.reduce(
                    (sum, user) => sum + getAccuracyPercentage(user),
                    0,
                  ) / users.length,
                )
              : 0}
            %
          </div>
          <div className="text-gray-600">Average Accuracy</div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        {users.length === 0 ? (
          <div className="py-12 text-center">
            <div className="mb-4 text-lg text-gray-500">No traders yet</div>
            <p className="text-gray-400">
              Be the first to start trading and claim the top spot!
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-gray-200 bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Rank
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Trader
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Level
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                    XP
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                    Trades
                  </th>
                  <th className="px-6 py-4 text-right text-sm font-medium text-gray-900">
                    Accuracy
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-gray-900">
                    Badges
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {users.map((user, index) => {
                  const rank = index + 1;
                  const accuracy = getAccuracyPercentage(user);
                  const { level, title } = getXPLevel(user.xp);

                  return (
                    <tr
                      key={user.principal.toString()}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <span className="mr-2 text-2xl">
                            {getRankBadge(rank)}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            {rank}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-gray-900">
                            {user.username}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatPrincipal(user.principal.toString())}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div
                            className={`mr-3 flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white ${
                              level === 1
                                ? "bg-gray-400"
                                : level === 2
                                  ? "bg-green-500"
                                  : level === 3
                                    ? "bg-blue-500"
                                    : level === 4
                                      ? "bg-purple-500"
                                      : level === 5
                                        ? "bg-yellow-500"
                                        : "bg-red-500"
                            }`}
                          >
                            {level}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {title}
                            </div>
                            <div className="text-xs text-gray-500">
                              Level {level}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="text-sm font-medium text-gray-900">
                          {Number(user.xp).toLocaleString()}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {Number(user.total_trades).toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-500">
                            {Number(user.successful_predictions)} successful
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                            accuracy >= 70
                              ? "bg-green-100 text-green-800"
                              : accuracy >= 50
                                ? "bg-yellow-100 text-yellow-800"
                                : "bg-red-100 text-red-800"
                          }`}
                        >
                          {accuracy}%
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {user.badges.length === 0 ? (
                            <span className="text-xs text-gray-400">
                              No badges
                            </span>
                          ) : (
                            user.badges.slice(0, 3).map((badge, badgeIndex) => (
                              <span
                                key={badgeIndex}
                                className="inline-flex items-center rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800"
                              >
                                {badge}
                              </span>
                            ))
                          )}
                          {user.badges.length > 3 && (
                            <span className="text-xs text-gray-400">
                              +{user.badges.length - 3} more
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Achievement System Info */}
      <div className="mt-12 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50 p-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          How to Earn XP & Badges
        </h3>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <h4 className="mb-2 font-medium text-gray-900">
              Experience Points (XP)
            </h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Trading: 1 XP per $0.10 traded</li>
              <li>• Successful predictions: Bonus XP</li>
              <li>• Market creation: 50 XP per validated market</li>
              <li>• Community engagement: Comments & discussions</li>
            </ul>
          </div>

          <div>
            <h4 className="mb-2 font-medium text-gray-900">Available Badges</h4>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>
                🎯 <strong>Sharpshooter:</strong> 80%+ accuracy over 20 trades
              </li>
              <li>
                📈 <strong>Bull Run:</strong> 10 consecutive winning trades
              </li>
              <li>
                🏭 <strong>Market Maker:</strong> Create 5 validated markets
              </li>
              <li>
                💬 <strong>Community Voice:</strong> 100+ helpful comments
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
