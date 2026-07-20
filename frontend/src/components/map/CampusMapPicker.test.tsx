import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CampusMapPicker } from "./CampusMapPicker";

vi.mock("@/hooks/useDeliveryZone", () => ({
  useDeliveryZone: () => ({ data: null }),
}));

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("CampusMapPicker", () => {
  it("falls back to a notice instead of crashing when no Google Maps API key is configured", () => {
    // @react-google-maps/api's Loader is a module-level singleton that throws
    // if re-initialized with different options, so this env is stubbed rather
    // than tested alongside a "key present" case in the same file/run.
    vi.stubEnv("VITE_GOOGLE_MAPS_API_KEY", "");
    render(<CampusMapPicker value={null} onChange={vi.fn()} />);
    expect(screen.getByText(/map picker isn't configured/i)).toBeInTheDocument();
  });
});
