"use client";

import { motion } from "motion/react";
import { Card } from "@/components/ui/card";
import {
  Briefcase,
  Star,
  Eye,
  Send,
} from "lucide-react";
import type { DashboardStats } from "@/lib/api";

interface StatsCardsProps {
  stats: DashboardStats | null;
}

const statConfig = [
  {
    key: "total_jobs" as const,
    label: "Total Jobs",
    icon: Briefcase,
    color: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-100",
  },
  {
    key: "high_priority" as const,
    label: "High Priority",
    icon: Star,
    color: "text-emerald-600",
    bg: "bg-emerald-50",
    border: "border-emerald-100",
  },
  {
    key: "review" as const,
    label: "Review",
    icon: Eye,
    color: "text-amber-600",
    bg: "bg-amber-50",
    border: "border-amber-100",
  },
  {
    key: "applications" as const,
    label: "Applied",
    icon: Send,
    color: "text-violet-600",
    bg: "bg-violet-50",
    border: "border-violet-100",
  },
];

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {statConfig.map((item, i) => (
        <motion.div
          key={item.key}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: i * 0.05 }}
        >
          <Card className={`p-4 border ${item.border} shadow-none hover:shadow-md transition-shadow duration-300`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
                  {item.label}
                </p>
                <p className="text-2xl font-bold mt-1 text-foreground">
                  {stats?.[item.key] ?? "—"}
                </p>
              </div>
              <div className={`w-9 h-9 rounded-lg ${item.bg} flex items-center justify-center`}>
                <item.icon className={`w-4 h-4 ${item.color}`} />
              </div>
            </div>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
