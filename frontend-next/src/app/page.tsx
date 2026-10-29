"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "motion/react";
import {
  getStats,
  getJobs,
  fetchNewJobs,
  runMatching,
  sendNotifications,
  type DashboardStats,
  type Job,
} from "@/lib/api";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { SourceChart } from "@/components/dashboard/source-chart";
import { ScoreChart } from "@/components/dashboard/score-chart";
import { PriorityJobs } from "@/components/dashboard/priority-jobs";
import { ActionBar } from "@/components/dashboard/action-bar";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [highJobs, setHighJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState<{
    message: string;
    type: "loading" | "success" | "error";
  } | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [statsData, jobsData] = await Promise.all([
        getStats(),
        getJobs("HIGH", 5),
      ]);
      setStats(statsData);
      setHighJobs(jobsData.jobs);
    } catch (err) {
      console.error("Dashboard load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleFetchJobs = async () => {
    setActionStatus({ message: "Fetching jobs from all sources...", type: "loading" });
    try {
      const data = await fetchNewJobs();
      setActionStatus({
        message: `Fetched ${data.total_fetched} jobs, ${data.new_jobs} new added`,
        type: "success",
      });
      loadData();
    } catch (err) {
      setActionStatus({
        message: `Fetch failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
      });
    }
  };

  const handleRunMatching = async () => {
    setActionStatus({
      message: "Running AI matching... this may take a few minutes",
      type: "loading",
    });
    try {
      const data = await runMatching();
      const r = data.results;
      setActionStatus({
        message: `Matched ${r.processed} jobs — ${r.high_priority} high priority, ${r.review} review`,
        type: "success",
      });
      loadData();
    } catch (err) {
      setActionStatus({
        message: `Matching failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
      });
    }
  };

  const handleNotify = async () => {
    setActionStatus({ message: "Sending notifications...", type: "loading" });
    try {
      await sendNotifications();
      setActionStatus({ message: "Notifications sent successfully", type: "success" });
    } catch (err) {
      setActionStatus({
        message: `Notification failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
      });
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
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
      className="space-y-6"
    >
      {/* Stats Cards */}
      <StatsCards stats={stats} />

      {/* Action Bar */}
      <ActionBar
        onFetchJobs={handleFetchJobs}
        onRunMatching={handleRunMatching}
        onNotify={handleNotify}
        status={actionStatus}
      />

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <SourceChart bySource={stats?.by_source || {}} />
        <ScoreChart stats={stats} />
      </div>

      {/* Priority Jobs */}
      <PriorityJobs jobs={highJobs} onRefresh={loadData} />
    </motion.div>
  );
}
