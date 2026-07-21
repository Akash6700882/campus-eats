import { Check, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ORDER_STATUS_LABELS } from "@/lib/format";
import type { OrderStatus } from "@/types";

// "accepted"/"preparing" are omitted here — paid orders auto-confirm
// straight from "pending" to "ready" (no kitchen-confirmation gate), so
// showing them as distinct customer-facing steps would falsely imply a
// manual approval that never happened. They remain valid OrderStatus
// values for the (unpaid-only) kitchen API, just not part of this timeline.
const TIMELINE_STEPS: OrderStatus[] = ["pending", "ready", "assigned", "picked_up", "on_the_way", "delivered"];

export function StatusTimeline({ status }: { status: OrderStatus }) {
  if (status === "cancelled" || status === "refunded") {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm font-medium text-destructive">
        <X className="h-4 w-4" />
        {status === "cancelled" ? "This order was cancelled." : "This order was refunded."}
      </div>
    );
  }

  const currentIndex = TIMELINE_STEPS.indexOf(status);

  return (
    <ol className="space-y-0">
      {TIMELINE_STEPS.map((step, index) => {
        const done = index < currentIndex;
        const active = index === currentIndex;
        return (
          <li key={step} className="flex gap-3">
            <div className="flex flex-col items-center">
              <span
                className={cn(
                  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 text-xs",
                  done && "border-primary bg-primary text-primary-foreground",
                  active && "border-primary text-primary",
                  !done && !active && "border-muted-foreground/30 text-muted-foreground",
                )}
              >
                {done ? <Check className="h-3.5 w-3.5" /> : index + 1}
              </span>
              {index < TIMELINE_STEPS.length - 1 && (
                <span className={cn("h-8 w-0.5", done ? "bg-primary" : "bg-muted-foreground/20")} />
              )}
            </div>
            <p
              className={cn(
                "pb-6 text-sm",
                (done || active) && "font-medium text-foreground",
                !done && !active && "text-muted-foreground",
              )}
            >
              {ORDER_STATUS_LABELS[step]}
            </p>
          </li>
        );
      })}
    </ol>
  );
}
