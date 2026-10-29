"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "motion/react";
import { getApplications, type Application } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  ExternalLink,
  Calendar,
  Wrench,
  MapPin,
  ClipboardList,
} from "lucide-react";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  const loadApplications = useCallback(async () => {
    try {
      const data = await getApplications();
      setApplications(data.applications);
    } catch (err) {
      console.error("Applications load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadApplications();
  }, [loadApplications]);

  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      <p className="text-[11px] text-muted-foreground">
        {applications.length} {applications.length === 1 ? "application" : "applications"} tracked
      </p>

      {applications.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mx-auto mb-3">
            <ClipboardList className="w-5 h-5 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-foreground">No applications yet</p>
          <p className="text-xs text-muted-foreground mt-1">
            Mark jobs as applied from the Jobs page to track them here.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app, i) => (
            <motion.div
              key={app.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: i * 0.03 }}
            >
              <Card className="p-4 shadow-none border hover:shadow-md transition-shadow duration-200">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-[13px] font-semibold text-foreground truncate">
                      {app.title}
                    </h3>
                    <p className="text-[12px] text-muted-foreground mt-0.5">
                      {app.company}
                    </p>
                  </div>
                  <Badge
                    variant="secondary"
                    className="text-[10px] font-semibold bg-emerald-50 text-emerald-700 border-emerald-200 shrink-0"
                  >
                    {app.status}
                  </Badge>
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2.5 text-[11px] text-muted-foreground">
                  {app.applied_at && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      Applied: {new Date(app.applied_at).toLocaleDateString()}
                    </span>
                  )}
                  {app.method && (
                    <span className="flex items-center gap-1">
                      <Wrench className="w-3 h-3" />
                      {app.method}
                    </span>
                  )}
                  {app.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {app.location}
                    </span>
                  )}
                </div>

                {app.notes && (
                  <p className="text-[11px] text-muted-foreground mt-2 line-clamp-2">
                    {app.notes}
                  </p>
                )}

                <div className="mt-3 pt-3 border-t border-border/50">
                  <a
                    href={app.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-[11px] font-medium text-primary hover:text-primary/80 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    View Job Posting
                  </a>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
