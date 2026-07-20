import { describe, expect, it } from "vitest";
import { formatCurrency, formatDateTime, ORDER_STATUS_LABELS } from "./format";

describe("formatCurrency", () => {
  it("formats a whole number as INR", () => {
    expect(formatCurrency(100)).toBe("₹100.00");
  });

  it("formats a decimal amount", () => {
    expect(formatCurrency(114.5)).toBe("₹114.50");
  });

  it("formats zero", () => {
    expect(formatCurrency(0)).toBe("₹0.00");
  });
});

describe("formatDateTime", () => {
  it("renders a readable date and time", () => {
    const result = formatDateTime("2026-07-20T05:19:00Z");
    expect(result).toMatch(/\d{1,2}:\d{2}/);
    expect(result).toMatch(/Jul/);
  });
});

describe("ORDER_STATUS_LABELS", () => {
  it("has a human-readable label for every backend order status", () => {
    const statuses = [
      "pending",
      "accepted",
      "preparing",
      "ready",
      "assigned",
      "picked_up",
      "on_the_way",
      "delivered",
      "cancelled",
      "refunded",
    ];
    for (const status of statuses) {
      expect(ORDER_STATUS_LABELS[status]).toBeTruthy();
    }
  });
});
