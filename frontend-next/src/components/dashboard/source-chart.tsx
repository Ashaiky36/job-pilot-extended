"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

interface SourceChartProps {
  bySource: Record<string, number>;
}

const COLORS = [
  "oklch(0.488 0.180 264)",
  "oklch(0.696 0.170 162)",
  "oklch(0.769 0.170 80)",
  "oklch(0.627 0.265 303)",
  "oklch(0.645 0.200 16)",
];

export function SourceChart({ bySource }: SourceChartProps) {
  const data = Object.entries(bySource).map(([name, value]) => ({
    name: name.length > 12 ? name.slice(0, 12) + "…" : name,
    fullName: name,
    count: value,
  }));

  if (data.length === 0) {
    return (
      <Card className="shadow-none border">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-semibold">Jobs by Source</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-xs text-muted-foreground">
            No data yet — fetch jobs to populate
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-none border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Jobs by Source</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.9 0 0)" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: "oklch(0.5 0 0)" }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "oklch(0.5 0 0)" }}
              axisLine={false}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                background: "white",
                border: "1px solid oklch(0.92 0 0)",
                borderRadius: "8px",
                fontSize: "12px",
                boxShadow: "0 4px 12px oklch(0 0 0 / 8%)",
              }}
              formatter={(value) => [value, "Jobs"]}
              labelFormatter={(_label, payload) => {
                const item = payload?.[0]?.payload;
                return item?.fullName || String(_label);
              }}
            />
            <Bar dataKey="count" radius={[6, 6, 0, 0]} barSize={32}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
