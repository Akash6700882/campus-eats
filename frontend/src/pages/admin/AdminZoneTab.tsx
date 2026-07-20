import { DeliveryZoneEditor } from "@/components/map/DeliveryZoneEditor";

export function AdminZoneTab() {
  return (
    <div>
      <h2 className="mb-3 font-heading text-lg font-semibold">Delivery zone</h2>
      <DeliveryZoneEditor />
    </div>
  );
}
