import type { ReactNode } from "react";

export function MapStatusNotice({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full min-h-[220px] items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 p-6 text-center text-sm text-muted-foreground">
      {children}
    </div>
  );
}
