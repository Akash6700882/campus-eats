import { useState } from "react";
import { LogOut, MapPin, Plus, Trash2, User as UserIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AddressForm } from "@/components/address/AddressForm";
import { useAddresses, useAddressMutations } from "@/hooks/useAddresses";
import { useAuth } from "@/store/auth";

export function ProfilePage() {
  const { user, logout } = useAuth();
  const { data: addresses, isLoading } = useAddresses();
  const { remove } = useAddressMutations();
  const [showAddForm, setShowAddForm] = useState(false);

  return (
    <div className="container max-w-2xl py-8">
      <h1 className="font-heading text-2xl font-bold">Profile</h1>

      <Card className="mt-6">
        <CardContent className="flex flex-wrap items-center justify-between gap-3 py-4">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-accent-foreground">
              <UserIcon className="h-6 w-6" />
            </span>
            <div>
              <p className="font-medium">{user?.full_name}</p>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <p className="text-sm text-muted-foreground">{user?.phone}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4" /> Log out
          </Button>
        </CardContent>
      </Card>

      <div className="mt-8 flex items-center justify-between">
        <h2 className="flex items-center gap-1.5 font-heading text-lg font-semibold">
          <MapPin className="h-5 w-5" /> Saved addresses
        </h2>
        <Button variant="ghost" size="sm" onClick={() => setShowAddForm((s) => !s)}>
          <Plus className="h-4 w-4" /> {showAddForm ? "Cancel" : "Add new"}
        </Button>
      </div>

      {showAddForm && (
        <Card className="mt-3">
          <CardContent className="py-4">
            <AddressForm onCreated={() => setShowAddForm(false)} />
          </CardContent>
        </Card>
      )}

      {!isLoading && addresses && addresses.length === 0 && !showAddForm && (
        <p className="mt-3 text-sm text-muted-foreground">No saved addresses yet.</p>
      )}

      <div className="mt-3 space-y-2">
        {addresses?.map((address) => (
          <Card key={address.id}>
            <CardContent className="flex items-center justify-between py-3">
              <div className="text-sm">
                <p className="font-medium">
                  {address.label}
                  {address.is_default && <span className="ml-2 text-xs text-muted-foreground">(default)</span>}
                </p>
                <p className="text-muted-foreground">
                  {[
                    address.hostel,
                    address.building,
                    address.block && `Block ${address.block}`,
                    address.room_number && `Room ${address.room_number}`,
                    address.department,
                  ]
                    .filter(Boolean)
                    .join(", ") || "No extra details"}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                className="text-muted-foreground hover:text-destructive"
                onClick={() => remove.mutate(address.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
