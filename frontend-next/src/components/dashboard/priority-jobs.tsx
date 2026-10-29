"use client";

import { motion } from "motion/react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { JobCard } from "@/components/jobs/job-card";
import type { Job } from "@/lib/api";
import { Star } from "lucide-react";

interface PriorityJobsProps {
  jobs: Job[];
  onRefresh: () => void;
}

export function PriorityJobs({ jobs, onRefresh }: PriorityJobsProps) {
  return (
    <Card className="shadow-none border">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          <Star className="w-4 h-4 text-emerald-500" />
          Top Priority Matches
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {jobs.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-xs text-muted-foreground">
              No high priority jobs yet. Fetch jobs and run AI matching to get started.
            </p>
          </div>
        ) : (
          jobs.map((job, i) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: i * 0.04 }}
            >
              <JobCard job={job} onApplied={onRefresh} />
            </motion.div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
