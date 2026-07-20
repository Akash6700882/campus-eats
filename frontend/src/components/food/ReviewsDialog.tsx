import { type ReactNode, useState } from "react";
import { Loader2, ThumbsUp, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { StarRatingInput } from "@/components/food/StarRatingInput";
import { useFoodReviews, useReviewActions } from "@/hooks/useReviews";
import { useAuth } from "@/store/auth";
import { formatDateTime } from "@/lib/format";
import type { Food } from "@/types";

export function ReviewsDialog({ food, children }: { food: Food; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const { isAuthenticated } = useAuth();

  const { data: reviews, isLoading } = useFoodReviews(food.id, open);
  const { create, toggleLike } = useReviewActions(food.id);

  function handleSubmit() {
    if (rating === 0) return;
    create.mutate(
      { rating, comment: comment || undefined },
      {
        onSuccess: () => {
          setShowForm(false);
          setRating(0);
          setComment("");
        },
      },
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="max-h-[80vh] overflow-y-auto sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{food.name} — Reviews</DialogTitle>
        </DialogHeader>

        {isAuthenticated && (
          <div>
            {!showForm ? (
              <Button variant="outline" size="sm" onClick={() => setShowForm(true)}>
                Write a review
              </Button>
            ) : (
              <div className="space-y-3 rounded-lg border border-border p-3">
                <StarRatingInput value={rating} onChange={setRating} />
                <Textarea
                  placeholder="How was it? (optional)"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button size="sm" disabled={rating === 0 || create.isPending} onClick={handleSubmit}>
                    {create.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                    Submit
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setShowForm(false)}>
                    Cancel
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  You can review food you've received in a delivered order.
                </p>
              </div>
            )}
            <Separator className="my-4" />
          </div>
        )}

        {isLoading && <p className="text-sm text-muted-foreground">Loading reviews...</p>}
        {!isLoading && (!reviews || reviews.length === 0) && (
          <p className="text-sm text-muted-foreground">No reviews yet — be the first!</p>
        )}
        <div className="space-y-4">
          {reviews?.map((review) => (
            <div key={review.id} className="space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5 text-muted-foreground" />
                  <span className="text-sm font-medium">{review.user_name}</span>
                </div>
                <StarRatingInput value={review.rating} readOnly />
              </div>
              {review.comment && <p className="text-sm text-muted-foreground">{review.comment}</p>}
              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                <span>{formatDateTime(review.created_at)}</span>
                <button
                  type="button"
                  className="flex items-center gap-1 hover:text-foreground"
                  onClick={() => isAuthenticated && toggleLike.mutate(review.id)}
                >
                  <ThumbsUp className="h-3 w-3" /> {review.likes_count}
                </button>
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
