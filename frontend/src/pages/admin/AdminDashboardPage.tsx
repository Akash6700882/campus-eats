import { LayoutDashboard } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AdminOrdersTab } from "@/pages/admin/AdminOrdersTab";
import { AdminPartnersTab } from "@/pages/admin/AdminPartnersTab";
import { AdminMenuTab } from "@/pages/admin/AdminMenuTab";

export function AdminDashboardPage() {
  return (
    <div className="container py-8">
      <h1 className="flex items-center gap-2 font-heading text-2xl font-bold">
        <LayoutDashboard className="h-6 w-6 text-primary" /> Admin dashboard
      </h1>

      <Tabs defaultValue="orders" className="mt-6">
        <TabsList>
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="partners">Delivery partners</TabsTrigger>
          <TabsTrigger value="menu">Menu</TabsTrigger>
        </TabsList>
        <TabsContent value="orders" className="mt-4">
          <AdminOrdersTab />
        </TabsContent>
        <TabsContent value="partners" className="mt-4">
          <AdminPartnersTab />
        </TabsContent>
        <TabsContent value="menu" className="mt-4">
          <AdminMenuTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
