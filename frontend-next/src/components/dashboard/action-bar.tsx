"use client";

import { Button } from "@/components/ui/button";
import { Search, Cpu, Bell, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ActionBarProps {
  onFetchJobs: () => void;
  onRunMatching: () => void;
  onNotify: () => void;
  status: { message: string; type: "loading" | "success" | "error" } | null;
}

export function ActionBar({ onFetchJobs, onRunMatching, onNotify, status }: ActionBarProps) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <Button
          onClick={onFetchJobs}
          size="sm"
          className="gap-2 text-xs h-8 bg-primary hover:bg-primary/90"
          disabled={status?.type === "loading"}
        >
          <Search className="w-3.5 h-3.5" />
          Fetch New Jobs
        </Button>
        <Button
          onClick={onRunMatching}
          size="sm"
          variant="outline"
          className="gap-2 text-xs h-8"
          disabled={status?.type === "loading"}
        >
          <Cpu className="w-3.5 h-3.5" />
          Run AI Matching
        </Button>
        <Button
          onClick={onNotify}
          size="sm"
          variant="outline"
          className="gap-2 text-xs h-8"
          disabled={status?.type === "loading"}
        >
          <Bell className="w-3.5 h-3.5" />
          Send Notifications
        </Button>
      </div>

      {status && (
        <div
          className={cn(
            "flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all",
            status.type === "loading" && "bg-blue-50 text-blue-700 border border-blue-100",
            status.type === "success" && "bg-emerald-50 text-emerald-700 border border-emerald-100",
            status.type === "error" && "bg-red-50 text-red-700 border border-red-100"
          )}
        >
          {status.type === "loading" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
          {status.type === "success" && <CheckCircle2 className="w-3.5 h-3.5" />}
          {status.type === "error" && <XCircle className="w-3.5 h-3.5" />}
          {status.message}
        </div>
      )}
    </div>
  );
}
