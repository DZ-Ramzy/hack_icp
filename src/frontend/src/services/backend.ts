import { backend } from "../../../declarations/backend";
import type {
  Market,
  Trade,
  UserProfile,
  AIInsight,
  MarketComment,
  MarketStatus,
} from "../../../declarations/backend/backend.did";
import { Principal } from "@dfinity/principal";

export interface MarketFilters {
  status?: "active" | "closed" | "resolved" | "pending";
  category?: string;
}

export class BackendService {
  // Market functions
  static async getMarkets(): Promise<Market[]> {
    try {
      const markets = await backend.get_markets();
      return markets;
    } catch (error) {
      console.error("Failed to fetch markets:", error);
      throw error;
    }
  }

  static async getMarket(id: bigint): Promise<Market | null> {
    try {
      const result = await backend.get_market(id);
      return Array.isArray(result) && result.length > 0
        ? result[0] || null
        : null;
    } catch (error) {
      console.error("Failed to fetch market:", error);
      throw error;
    }
  }

  static async createMarket(
    title: string,
    description: string,
    category: string,
    closeDate: bigint,
  ): Promise<bigint> {
    try {
      const result = await backend.create_market(
        title,
        description,
        category,
        closeDate,
      );
      if ("Ok" in result) {
        return result.Ok;
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error("Failed to create market:", error);
      throw error;
    }
  }

  // Trading functions
  static async buyShares(
    marketId: bigint,
    isYes: boolean,
    amount: bigint,
  ): Promise<Trade> {
    try {
      const result = await backend.buy_shares(marketId, isYes, amount);
      if ("Ok" in result) {
        return result.Ok;
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error("Failed to buy shares:", error);
      throw error;
    }
  }

  static async getMarketTrades(marketId: bigint): Promise<Trade[]> {
    try {
      return await backend.get_market_trades(marketId);
    } catch (error) {
      console.error("Failed to fetch market trades:", error);
      throw error;
    }
  }

  // User functions
  static async getUserProfile(
    principal: Principal,
  ): Promise<UserProfile | null> {
    try {
      const result = await backend.get_user_profile(principal as any);
      return Array.isArray(result) && result.length > 0
        ? result[0] || null
        : null;
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      throw error;
    }
  }

  static async getLeaderboard(): Promise<UserProfile[]> {
    try {
      return await backend.get_leaderboard();
    } catch (error) {
      console.error("Failed to fetch leaderboard:", error);
      throw error;
    }
  }

  // AI Insights
  static async getAIInsight(marketId: bigint): Promise<AIInsight | null> {
    try {
      const result = await backend.get_ai_insight(marketId);
      return Array.isArray(result) && result.length > 0
        ? result[0] || null
        : null;
    } catch (error) {
      console.error("Failed to fetch AI insight:", error);
      throw error;
    }
  }

  // Comments
  static async addComment(marketId: bigint, content: string): Promise<bigint> {
    try {
      const result = await backend.add_comment(marketId, content);
      if ("Ok" in result) {
        return result.Ok;
      } else {
        throw new Error(result.Err);
      }
    } catch (error) {
      console.error("Failed to add comment:", error);
      throw error;
    }
  }

  static async getMarketComments(marketId: bigint): Promise<MarketComment[]> {
    try {
      return await backend.get_market_comments(marketId);
    } catch (error) {
      console.error("Failed to fetch market comments:", error);
      throw error;
    }
  }

  // Utils
  static formatTimestamp(timestamp: bigint): string {
    const date = new Date(Number(timestamp) / 1000000); // Convert nanoseconds to milliseconds
    return date.toLocaleDateString();
  }

  static formatPrice(price: bigint): string {
    const numPrice = Number(price) / 1000; // Convert to decimal (0.000-1.000)
    return `$${numPrice.toFixed(3)}`;
  }

  static getMarketStatusText(status: MarketStatus): string {
    if ("Active" in status) return "Active";
    if ("Closed" in status) return "Closed";
    if ("Resolved" in status) return "Resolved";
    if ("PendingValidation" in status) return "Pending";
    return "Unknown";
  }

  static filterMarkets(markets: Market[], filters: MarketFilters): Market[] {
    return markets.filter((market) => {
      if (filters.status) {
        const statusText = this.getMarketStatusText(
          market.status,
        ).toLowerCase();
        if (statusText !== filters.status) return false;
      }

      if (filters.category && market.category !== filters.category) {
        return false;
      }

      return true;
    });
  }
}
