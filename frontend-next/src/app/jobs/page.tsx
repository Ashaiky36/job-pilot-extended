"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "motion/react";
import { getJobs, type Job } from "@/lib/api";
import { JobCard } from "@/components/jobs/job-card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Briefcase } from "lucide-react";

const filters = [
  { key: "all", label: "All Matches" },
  { key: "HIGH", label: "High Priority" },
  { key: "REVIEW", label: "Review" },
];

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  const loadJobs = useCallback(async (priority: string) => {
    setLoading(true);
    try {
      const data = await getJobs(priority, 50);
      setJobs(data.jobs);
    } catch (err) {
      console.error("Jobs load failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadJobs(filter);
  }, [filter, loadJobs]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      {/* Filter Bar */}
      <div className="flex items-center gap-1.5 p-1 bg-muted/50 rounded-lg w-fit">
        {filters.map((f) => (
          <Button
            key={f.key}
            variant="ghost"
            size="sm"
            onClick={() => setFilter(f.key)}
            className={cn(
              "h-7 px-3 text-xs font-medium rounded-md transition-all",
              filter === f.key
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {/* Count */}
      <p className="text-[11px] text-muted-foreground">
        {jobs.length} {jobs.length === 1 ? "job" : "jobs"} found
      </p>

      {/* Jobs List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center mx-auto mb-3">
            <Briefcase className="w-5 h-5 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-foreground">No jobs found</p>
          <p className="text-xs text-muted-foreground mt-1">
            Run job fetch and AI matching from the Dashboard first.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job, i) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: i * 0.03 }}
            >
              <JobCard job={job} onApplied={() => loadJobs(filter)} />
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
