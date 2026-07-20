import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StarRatingInput } from "./StarRatingInput";

describe("StarRatingInput", () => {
  it("calls onChange with the clicked star's value", () => {
    const onChange = vi.fn();
    render(<StarRatingInput value={0} onChange={onChange} />);

    fireEvent.click(screen.getByLabelText("4 stars"));

    expect(onChange).toHaveBeenCalledWith(4);
  });

  it("renders exactly 5 interactive stars when editable", () => {
    render(<StarRatingInput value={2} onChange={vi.fn()} />);
    expect(screen.getAllByRole("button")).toHaveLength(5);
  });

  it("renders no interactive buttons in read-only mode", () => {
    render(<StarRatingInput value={3} readOnly />);
    expect(screen.queryAllByRole("button")).toHaveLength(0);
  });
});
