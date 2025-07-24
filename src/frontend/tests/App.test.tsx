import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "../src/App";
import { StrictMode } from "react";

// Mock the auth service to avoid IndexedDB issues
vi.mock("../src/services/auth", () => ({
  AuthService: {
    init: vi.fn(),
    getAuthState: vi.fn().mockResolvedValue({
      isAuthenticated: false,
      principal: null,
      identity: null,
    }),
    addAuthListener: vi.fn(),
    removeAuthListener: vi.fn(),
  },
}));

// Mock the backend service
vi.mock("../src/services/backend", () => ({
  BackendService: {
    getMarkets: vi.fn().mockResolvedValue([]),
  },
}));

describe("App", () => {
  it("renders the main components", async () => {
    render(
      <StrictMode>
        <App />
      </StrictMode>,
    );

    // Check for unique UI elements that should always be present
    expect(screen.getByText("Connect wallet")).toBeInTheDocument();

    // ChainPredict appears multiple times (header + footer) so use getAllByText
    const chainPredictElements = screen.getAllByText("ChainPredict");
    expect(chainPredictElements.length).toBeGreaterThan(0);
  });
});
