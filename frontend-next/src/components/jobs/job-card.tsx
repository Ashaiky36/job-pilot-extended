"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  MapPin,
  ExternalLink,
  CheckCircle2,
  Lightbulb,
  Tag,
  Clock,
  DollarSign,
} from "lucide-react";
import { markApplied, type Job } from "@/lib/api";
import { useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface JobCardProps {
  job: Job;
  onApplied?: () => void;
}

export function JobCard({ job, onApplied }: JobCardProps) {
  const [applying, setApplying] = useState(false);
  const isHigh = job.priority === "HIGH";

  const handleApply = async () => {
    setApplying(true);
    try {
      await markApplied(job.id);
      onApplied?.();
    } catch (err) {
      console.error("Apply failed:", err);
    } finally {
      setApplying(false);
    }
  };

  return (
    <div
      className={cn(
        "group rounded-xl border bg-card p-4 transition-all duration-200 hover:shadow-md",
        isHigh ? "border-l-[3px] border-l-emerald-400" : "border-l-[3px] border-l-amber-400"
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-[13px] font-semibold text-foreground truncate">
            {job.title}
          </h3>
          <p className="text-[12px] text-muted-foreground mt-0.5">
            {job.company || "Unknown company"}
          </p>
        </div>
        <Badge
          variant="secondary"
          className={cn(
            "text-[10px] font-semibold shrink-0",
            isHigh
              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
              : "bg-amber-50 text-amber-700 border-amber-200"
          )}
        >
          {job.match_score || 0}% match
        </Badge>
      </div>

      {/* Meta */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2.5 text-[11px] text-muted-foreground">
        {job.location && (
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {job.location}
          </span>
        )}
        {job.source && (
          <span className="flex items-center gap-1">
            <Tag className="w-3 h-3" />
            {job.source}
          </span>
        )}
        {job.salary_range && (
          <span className="flex items-center gap-1">
            <DollarSign className="w-3 h-3" />
            {job.salary_range}
          </span>
        )}
        {job.job_type && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {job.job_type}
          </span>
        )}
      </div>

      {/* Skills */}
      {(job.matched_skills?.length > 0 || job.missing_required?.length > 0) && (
        <div className="flex flex-wrap gap-1 mt-2.5">
          {job.matched_skills?.slice(0, 5).map((skill) => (
            <span
              key={skill}
              className="px-1.5 py-0.5 rounded-md bg-primary/10 text-primary text-[10px] font-medium"
            >
              {skill}
            </span>
          ))}
          {job.missing_required?.slice(0, 3).map((skill) => (
            <span
              key={skill}
              className="px-1.5 py-0.5 rounded-md bg-red-50 text-red-600 text-[10px] font-medium"
            >
              ⚠ {skill}
            </span>
          ))}
        </div>
      )}

      {/* Recommendation */}
      {job.recommendation && (
        <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed line-clamp-2">
          {job.recommendation}
        </p>
      )}

      {/* Suggestions */}
      {job.improvement_suggestions?.length > 0 && (
        <div className="mt-2 space-y-0.5">
          {job.improvement_suggestions.slice(0, 2).map((s, i) => (
            <div key={i} className="flex items-start gap-1.5 text-[10px] text-muted-foreground">
              <Lightbulb className="w-3 h-3 mt-0.5 text-amber-500 shrink-0" />
              <span className="line-clamp-1">{s}</span>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/50">
        <Tooltip>
          <TooltipTrigger
            render={
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border text-[11px] font-medium text-muted-foreground hover:text-foreground hover:border-foreground/20 transition-colors"
              >
                <ExternalLink className="w-3 h-3" />
                View Job
              </a>
            }
          />
          <TooltipContent side="bottom" className="text-[10px]">
            Open job posting in new tab
          </TooltipContent>
        </Tooltip>

        <Button
          size="sm"
          variant="ghost"
          onClick={handleApply}
          disabled={applying}
          className="h-7 px-2.5 text-[11px] text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 gap-1.5"
        >
          <CheckCircle2 className="w-3 h-3" />
          {applying ? "Saving..." : "Mark Applied"}
        </Button>
      </div>
    </div>
  );
}
