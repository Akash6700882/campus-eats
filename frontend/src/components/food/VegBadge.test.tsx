import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VegBadge } from "./VegBadge";

describe("VegBadge", () => {
  it("renders a veg indicator with the correct title", () => {
    const { container } = render(<VegBadge isVeg />);
    expect(container.querySelector("[title='Vegetarian']")).toBeInTheDocument();
  });

  it("renders a non-veg indicator with the correct title", () => {
    const { container } = render(<VegBadge isVeg={false} />);
    expect(container.querySelector("[title='Non-vegetarian']")).toBeInTheDocument();
  });
});
