import { describe, beforeEach, afterEach, it, expect, inject } from "vitest";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { PocketIc, type Actor } from "@dfinity/pic";
import { Principal } from "@dfinity/principal";

// Import generated types for your canister
import {
  type _SERVICE,
  idlFactory,
} from "../../src/declarations/backend/backend.did.js";

// Define the path to your canister's WASM file
export const WASM_PATH = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
  "target",
  "wasm32-unknown-unknown",
  "release",
  "backend.wasm",
);

// The `describe` function is used to group tests together
describe("ChainPredict ICP Backend", () => {
  // Define variables to hold our PocketIC instance, canister ID,
  // and an actor to interact with our canister.
  let pic: PocketIc;
  // @ts-ignore - This variable is used in the setup / framework
  let canisterId: Principal;
  let actor: Actor<_SERVICE>;

  // The `beforeEach` hook runs before each test.
  beforeEach(async () => {
    // create a new PocketIC instance
    pic = await PocketIc.create(inject("PIC_URL"));

    // Setup the canister and actor
    const fixture = await pic.setupCanister<_SERVICE>({
      idlFactory,
      wasm: WASM_PATH,
    });

    // Save the actor and canister ID for use in tests
    actor = fixture.actor;
    canisterId = fixture.canisterId;
  });

  // The `afterEach` hook runs after each test.
  afterEach(async () => {
    // tear down the PocketIC instance
    await pic.tearDown();
  });

  // The `it` function is used to define individual tests
  it("should return sample markets on initialization", async () => {
    const markets = await actor.get_markets();
    expect(markets.length).toBeGreaterThan(0);
    // Check that at least one market contains Bitcoin in its title
    const bitcoinMarket = markets.find((m) => m.title.includes("Bitcoin"));
    expect(bitcoinMarket).toBeDefined();
  });

  it("should create a new market", async () => {
    const initialMarkets = await actor.get_markets();
    const initialCount = initialMarkets.length;

    const result = await actor.create_market(
      "Will AI replace developers by 2030?",
      "This market resolves to YES if AI can autonomously write, test, and deploy production software without human intervention.",
      "Technology",
      BigInt(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year from now
    );

    expect(result).toHaveProperty("Ok");

    const newMarkets = await actor.get_markets();
    expect(newMarkets.length).toBe(initialCount + 1);
  });

  it("should get specific market by ID", async () => {
    const market = await actor.get_market(BigInt(1));
    expect(market).toBeDefined();
    expect(market).toHaveLength(1); // Optional type returns array
    if (market && market.length > 0 && market[0]) {
      expect(market[0].id).toBe(BigInt(1));
      expect(market[0].title).toContain("Bitcoin");
    }
  });

  it("should handle buying shares", async () => {
    const initialMarket = await actor.get_market(BigInt(1));
    expect(initialMarket).toBeDefined();

    const tradeResult = await actor.buy_shares(BigInt(1), true, BigInt(100));
    expect(tradeResult).toHaveProperty("Ok");

    if (tradeResult && "Ok" in tradeResult) {
      const trade = tradeResult.Ok;
      expect(trade.market_id).toBe(BigInt(1));
      expect(trade.is_yes).toBe(true);
      expect(trade.shares).toBe(BigInt(100));
    }
  });

  it("should get AI insights for markets", async () => {
    const insight = await actor.get_ai_insight(BigInt(1));
    expect(insight).toBeDefined();
    if (insight && insight.length > 0 && insight[0]) {
      expect(insight[0].market_id).toBe(BigInt(1));
      expect(insight[0].summary).toBeDefined();
      expect(insight[0].confidence).toBeGreaterThan(0);
      expect(insight[0].risks).toBeInstanceOf(Array);
    }
  });

  it("should handle market comments", async () => {
    const commentResult = await actor.add_comment(
      BigInt(1),
      "This is a test comment about Bitcoin predictions.",
    );
    expect(commentResult).toHaveProperty("Ok");

    const comments = await actor.get_market_comments(BigInt(1));
    expect(comments.length).toBeGreaterThan(0);
    expect(comments[comments.length - 1].content).toContain("test comment");
  });

  it("should track treasury balance", async () => {
    const initialBalance = await actor.get_treasury_balance();
    expect(typeof initialBalance).toBe("bigint");

    // Make a trade to generate fees
    await actor.buy_shares(BigInt(1), true, BigInt(100));

    const newBalance = await actor.get_treasury_balance();
    expect(newBalance).toBeGreaterThan(initialBalance);
  });
});
