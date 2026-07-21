import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageSpinner } from "@/components/PageSpinner";
import { useAppSettings, useUpdateAppSettings } from "@/hooks/useAppSettings";

const settingsSchema = z.object({
  restaurant_name: z.string().min(1, "Required").max(120),
  gst_percent: z.coerce.number().min(0).max(100),
  delivery_charge: z.coerce.number().min(0),
  packing_charge: z.coerce.number().min(0),
  business_hours_open: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:MM"),
  business_hours_close: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:MM"),
});
type SettingsForm = z.infer<typeof settingsSchema>;

export function AdminSettingsTab() {
  const { data: settings, isLoading } = useAppSettings();
  const updateSettings = useUpdateAppSettings();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<SettingsForm>({ resolver: zodResolver(settingsSchema) });

  useEffect(() => {
    if (settings) reset(settings);
  }, [settings, reset]);

  if (isLoading || !settings) return <PageSpinner />;

  function onSubmit(values: SettingsForm) {
    updateSettings.mutate(values);
  }

  return (
    <Card className="max-w-xl">
      <CardContent className="py-4">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="restaurant_name">Restaurant name</Label>
            <Input id="restaurant_name" {...register("restaurant_name")} />
            {errors.restaurant_name && <p className="text-xs text-destructive">{errors.restaurant_name.message}</p>}
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="gst_percent">GST %</Label>
              <Input id="gst_percent" type="number" step="0.01" {...register("gst_percent")} />
              {errors.gst_percent && <p className="text-xs text-destructive">{errors.gst_percent.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="delivery_charge">Delivery charge (₹)</Label>
              <Input id="delivery_charge" type="number" step="0.01" {...register("delivery_charge")} />
              {errors.delivery_charge && (
                <p className="text-xs text-destructive">{errors.delivery_charge.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="packing_charge">Packing charge (₹)</Label>
              <Input id="packing_charge" type="number" step="0.01" {...register("packing_charge")} />
              {errors.packing_charge && (
                <p className="text-xs text-destructive">{errors.packing_charge.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="business_hours_open">Opens at</Label>
              <Input id="business_hours_open" type="time" {...register("business_hours_open")} />
              {errors.business_hours_open && (
                <p className="text-xs text-destructive">{errors.business_hours_open.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="business_hours_close">Closes at</Label>
              <Input id="business_hours_close" type="time" {...register("business_hours_close")} />
              {errors.business_hours_close && (
                <p className="text-xs text-destructive">{errors.business_hours_close.message}</p>
              )}
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            Business hours are informational only right now — checkout isn&apos;t blocked outside them.
          </p>

          <Button type="submit" disabled={!isDirty || updateSettings.isPending}>
            {updateSettings.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Save changes
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
