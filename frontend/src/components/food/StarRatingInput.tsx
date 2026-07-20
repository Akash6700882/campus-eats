import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

export function StarRatingInput({
  value,
  onChange,
  readOnly = false,
}: {
  value: number;
  onChange?: (rating: number) => void;
  readOnly?: boolean;
}) {
  if (readOnly) {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star key={star} className={cn("h-4 w-4", star <= value ? "fill-primary text-primary" : "text-muted-foreground")} />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button key={star} type="button" onClick={() => onChange?.(star)} aria-label={`${star} star${star > 1 ? "s" : ""}`}>
          <Star className={cn("h-6 w-6 transition-colors", star <= value ? "fill-primary text-primary" : "text-muted-foreground")} />
        </button>
      ))}
    </div>
  );
}
