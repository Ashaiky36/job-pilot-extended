"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import type { DashboardStats } from "@/lib/api";

interface ScoreChartProps {
  stats: DashboardStats | null;
}

const COLORS = {
  high: "oklch(0.696 0.170 162)",
  review: "oklch(0.769 0.170 80)",
  skipped: "oklch(0.75 0 0)",
};

export function ScoreChart({ stats }: ScoreChartProps) {
  if (!stats || stats.processed_jobs === 0) {
    return (
      <Card className="shadow-none border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold">Match Distribution</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-xs text-muted-foreground">
            No matches yet — run AI matching first
          </p>
        </CardContent>
      </Card>
    );
  }

  const data = [
    { name: "High Priority", value: stats.high_priority, color: COLORS.high },
    { name: "Review", value: stats.review, color: COLORS.review },
    { name: "Skipped", value: stats.skipped, color: COLORS.skipped },
  ].filter((d) => d.value > 0);

  return (
    <Card className="shadow-none border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Match Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
              strokeWidth={0}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "white",
                border: "1px solid oklch(0.92 0 0)",
                borderRadius: "8px",
                fontSize: "12px",
                boxShadow: "0 4px 12px oklch(0 0 0 / 8%)",
              }}
              formatter={(value) => [value, "Jobs"]}
            />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: "11px" }}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
