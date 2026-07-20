import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { LocateFixed, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAddressMutations } from "@/hooks/useAddresses";
import { CampusMapPicker } from "@/components/map/CampusMapPicker";
import type { Address } from "@/types";

const addressSchema = z.object({
  label: z.string().min(1, "Give this address a label").max(50),
  hostel: z.string().optional(),
  building: z.string().optional(),
  block: z.string().optional(),
  room_number: z.string().optional(),
  department: z.string().optional(),
  notes: z.string().optional(),
});
type AddressFormValues = z.infer<typeof addressSchema>;

export function AddressForm({ onCreated }: { onCreated?: (address: Address) => void }) {
  const { create } = useAddressMutations();
  const [coords, setCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locating, setLocating] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AddressFormValues>({
    resolver: zodResolver(addressSchema),
    defaultValues: { label: "Hostel" },
  });

  function captureLocation() {
    if (!navigator.geolocation) {
      toast.error("Your browser doesn't support location detection");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
        setLocating(false);
      },
      () => {
        toast.error("Could not detect your location — allow location access and try again");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10_000 },
    );
  }

  async function onSubmit(values: AddressFormValues) {
    if (!coords) {
      toast.error("Capture your location before saving the address");
      return;
    }
    try {
      const address = await create.mutateAsync({ ...values, ...coords });
      toast.success("Address saved");
      onCreated?.(address);
    } catch {
      // surfaced by the mutation's onError toast
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label htmlFor="label">Label</Label>
          <Input id="label" placeholder="Hostel / Department" {...register("label")} />
          {errors.label && <p className="text-xs text-destructive">{errors.label.message}</p>}
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="hostel">Hostel</Label>
          <Input id="hostel" {...register("hostel")} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="building">Building</Label>
          <Input id="building" {...register("building")} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="block">Block</Label>
          <Input id="block" {...register("block")} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="room_number">Room number</Label>
          <Input id="room_number" {...register("room_number")} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="department">Department</Label>
          <Input id="department" {...register("department")} />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="notes">Notes for the delivery partner (optional)</Label>
        <Textarea id="notes" placeholder="e.g. Near the west gate, ask for room 204" {...register("notes")} />
      </div>

      <div className="space-y-2 rounded-lg border border-dashed border-input p-3">
        <p className="text-xs text-muted-foreground">
          Drag the pin to your exact spot on campus, or use your current location.
        </p>
        <CampusMapPicker value={coords} onChange={setCoords} />
        <Button type="button" variant="outline" size="sm" onClick={captureLocation} disabled={locating}>
          {locating ? <Loader2 className="h-4 w-4 animate-spin" /> : <LocateFixed className="h-4 w-4" />}
          {coords ? "Update my location" : "Use my current location"}
        </Button>
        {coords && (
          <p className="text-xs text-muted-foreground">
            Location captured ({coords.latitude.toFixed(5)}, {coords.longitude.toFixed(5)})
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          We only deliver inside campus — your location is checked against the campus boundary at checkout.
        </p>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting || create.isPending}>
        {(isSubmitting || create.isPending) && <Loader2 className="h-4 w-4 animate-spin" />}
        Save address
      </Button>
    </form>
  );
}
