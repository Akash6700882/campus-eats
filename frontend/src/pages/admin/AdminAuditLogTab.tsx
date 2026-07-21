import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { PageSpinner } from "@/components/PageSpinner";
import { useAuditLogs } from "@/hooks/useAdmin";
import { formatDateTime } from "@/lib/format";
import type { AuditLogEntry } from "@/types";

const ACTION_LABELS: Record<string, string> = {
  "user.block": "Blocked user",
  "user.unblock": "Unblocked user",
  "user.delete": "Deleted user",
  "user.reset_password": "Reset password",
  "order.force_cancel": "Force-cancelled order",
  "order.assign_partner": "Assigned delivery partner",
  "delivery_partner.create": "Created delivery partner",
  "delivery_zone.update": "Updated delivery zone",
};

function formatDetails(details: string | null): string | null {
  if (!details) return null;
  try {
    const parsed = JSON.parse(details) as Record<string, unknown>;
    return Object.entries(parsed)
      .map(([key, value]) => `${key}: ${value}`)
      .join(", ");
  } catch {
    return details;
  }
}

function AuditLogRow({ entry }: { entry: AuditLogEntry }) {
  const details = formatDetails(entry.details);
  return (
    <Card>
      <CardContent className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
        <div className="min-w-0">
          <p className="font-medium">{ACTION_LABELS[entry.action] ?? entry.action}</p>
          <p className="text-xs text-muted-foreground">
            {entry.actor_name} &middot; {formatDateTime(entry.created_at)}
          </p>
        </div>
        {details && <p className="text-xs text-muted-foreground">{details}</p>}
        <Badge variant="secondary" className="capitalize">
          {entry.target_type}
        </Badge>
      </CardContent>
    </Card>
  );
}

export function AdminAuditLogTab() {
  const { data: logs, isLoading } = useAuditLogs();

  if (isLoading) return <PageSpinner />;

  if (!logs || logs.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        No admin actions recorded yet.
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {logs.map((entry) => (
        <AuditLogRow key={entry.id} entry={entry} />
      ))}
    </div>
  );
}
