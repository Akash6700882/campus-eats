import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StarRatingInput } from "@/components/food/StarRatingInput";
import { useReviewActions } from "@/hooks/useReviews";
import type { OrderItem } from "@/types";

export function RateOrderItem({ orderId, item }: { orderId: string; item: OrderItem }) {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const { create } = useReviewActions(item.food_id);

  if (submitted) {
    return (
      <div className="flex items-center justify-between rounded-lg border border-border p-3 text-sm">
        <span>{item.food_name}</span>
        <span className="text-success">Thanks for rating!</span>
      </div>
    );
  }

  return (
    <div className="space-y-2 rounded-lg border border-border p-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{item.food_name}</span>
        <StarRatingInput value={rating} onChange={setRating} />
      </div>
      {rating > 0 && (
        <div className="flex gap-2">
          <Input
            placeholder="Add a comment (optional)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
          <Button
            size="sm"
            disabled={create.isPending}
            onClick={() =>
              create.mutate(
                { rating, comment: comment || undefined, order_id: orderId },
                { onSuccess: () => setSubmitted(true) },
              )
            }
          >
            {create.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
            Submit
          </Button>
        </div>
      )}
    </div>
  );
}
