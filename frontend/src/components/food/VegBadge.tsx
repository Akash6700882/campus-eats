export function VegBadge({ isVeg }: { isVeg: boolean }) {
  return (
    <span
      className={`inline-flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-[3px] border ${
        isVeg ? "border-success" : "border-destructive"
      }`}
      title={isVeg ? "Vegetarian" : "Non-vegetarian"}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${isVeg ? "bg-success" : "bg-destructive"}`} />
    </span>
  );
}
