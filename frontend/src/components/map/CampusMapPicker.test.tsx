import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CampusMapPicker } from "./CampusMapPicker";

vi.mock("@/hooks/useDeliveryZone", () => ({
  useDeliveryZone: () => ({ data: null }),
}));

describe("CampusMapPicker", () => {
  it("falls back to a notice instead of crashing when no Google Maps API key is configured", () => {
    render(<CampusMapPicker value={null} onChange={vi.fn()} />);
    expect(screen.getByText(/map picker isn't configured/i)).toBeInTheDocument();
  });
});
