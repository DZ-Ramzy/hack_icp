import "@testing-library/jest-dom/vitest";
import "@testing-library/jest-dom";
import "cross-fetch/polyfill";
import { vi } from "vitest";

// Mock console.error globally to suppress error logs in tests
// This prevents expected errors from cluttering test output
vi.spyOn(console, "error").mockImplementation(() => {});

// Mock IndexedDB for tests
const mockIDBRequest = {
  result: undefined,
  error: null,
  source: null,
  transaction: null,
  readyState: "done",
  onsuccess: null,
  onerror: null,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
};

global.indexedDB = {
  open: vi.fn().mockReturnValue(mockIDBRequest),
  deleteDatabase: vi.fn().mockReturnValue(mockIDBRequest),
  databases: vi.fn().mockResolvedValue([]),
} as any;

// Mock IDBKeyRange
global.IDBKeyRange = {
  bound: vi.fn(),
  only: vi.fn(),
  lowerBound: vi.fn(),
  upperBound: vi.fn(),
} as any;

// Mock IDBRequest
global.IDBRequest = function () {
  return mockIDBRequest;
} as any;

// Mock IDBTransaction
global.IDBTransaction = function () {} as any;

// Mock IDBDatabase
global.IDBDatabase = function () {} as any;

// Suppress "punnycode" deprecation warning
// while jsdom package doesn't find an alternative
process.removeAllListeners("warning");
process.on("warning", (warning) => {
  // Suppress DEP0040 warnings specifically
  if ((warning as any).code !== "DEP0040") {
    console.warn(warning.stack);
  }
});
