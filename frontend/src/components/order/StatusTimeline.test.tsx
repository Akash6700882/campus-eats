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
    render(<StatusTimeline status="assigned" />);
    expect(screen.getByText("Order placed")).toBeInTheDocument();
    expect(screen.getByText("Order confirmed")).toBeInTheDocument();
    expect(screen.getByText("Delivery partner assigned")).toBeInTheDocument();
    expect(screen.getByText("Delivered")).toBeInTheDocument();
  });

  it("doesn't show the kitchen-confirmation steps — paid orders auto-skip them", () => {
    render(<StatusTimeline status="assigned" />);
    expect(screen.queryByText("Accepted by kitchen")).not.toBeInTheDocument();
    expect(screen.queryByText("Preparing")).not.toBeInTheDocument();
  });
});
