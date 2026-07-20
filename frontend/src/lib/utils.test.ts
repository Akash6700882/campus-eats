import { describe, expect, it } from "vitest";
import { cn } from "./utils";

describe("cn", () => {
  it("joins truthy class names", () => {
    expect(cn("a", "b")).toBe("a b");
  });

  it("drops falsy values", () => {
    const isActive = false;
    expect(cn("a", isActive && "b", undefined, null, "c")).toBe("a c");
  });

  it("merges conflicting tailwind classes, keeping the last one", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("applies conditional classes from an object", () => {
    expect(cn("base", { active: true, hidden: false })).toBe("base active");
  });
});
