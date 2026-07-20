import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusTimeline } from "./StatusTimeline";

describe("StatusTimeline", () => {
  it("shows a cancelled banner instead of the step list when cancelled", () => {
    render(<StatusTimeline status="cancelled" />);
    expect(screen.getByText("This order was cancelled.")).toBeInTheDocument();
    expect(screen.queryByText("Order placed")).not.toBeInTheDocument();
  });

  it("shows a refunded banner when refunded", () => {
    render(<StatusTimeline status="refunded" />);
    expect(screen.getByText("This order was refunded.")).toBeInTheDocument();
  });

  it("renders every step label for an in-progress order", () => {
    render(<StatusTimeline status="preparing" />);
    expect(screen.getByText("Order placed")).toBeInTheDocument();
    expect(screen.getByText("Accepted by kitchen")).toBeInTheDocument();
    expect(screen.getByText("Preparing")).toBeInTheDocument();
    expect(screen.getByText("Delivered")).toBeInTheDocument();
  });
});
