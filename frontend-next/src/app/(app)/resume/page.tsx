"use client";

import { useState, useRef, useCallback } from "react";
import { motion } from "motion/react";
import { uploadResume, type ResumeUploadResult } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  Upload,
  FileText,
  Loader2,
  CheckCircle2,
  XCircle,
  User,
  Sparkles,
} from "lucide-react";

const roleOptions = [
  { value: "data_analyst", label: "Data Analyst" },
  { value: "data_scientist", label: "Data Scientist" },
  { value: "ml_engineer", label: "ML Engineer / AI Engineer" },
  { value: "data_engineer", label: "Data Engineer" },
];

export default function ResumePage() {
  const [roleType, setRoleType] = useState("data_analyst");
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<{
    message: string;
    type: "success" | "error";
  } | null>(null);
  const [preview, setPreview] = useState<ResumeUploadResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".pdf") && !file.name.endsWith(".docx")) {
        setStatus({ message: "Only PDF and DOCX files are supported", type: "error" });
        return;
      }

      setUploading(true);
      setStatus(null);
      setPreview(null);

      try {
        const data = await uploadResume(file, roleType);
        if (data.success) {
          setStatus({
            message: `Resume uploaded for ${roleType.replace(/_/g, " ")}`,
            type: "success",
          });
          setPreview(data);
        }
      } catch (err) {
        setStatus({
          message: err instanceof Error ? err.message : "Upload failed",
          type: "error",
        });
      } finally {
        setUploading(false);
      }
    },
    [roleType]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      const file = e.dataTransfer.files[0];
      if (file) handleUpload(file);
    },
    [handleUpload]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => setDragActive(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="max-w-xl space-y-5"
    >
      <Card className="p-5 shadow-none border">
        <h2 className="text-sm font-semibold text-foreground mb-1">
          Upload Resume
        </h2>
        <p className="text-[11px] text-muted-foreground mb-4">
          Upload different resume versions for different roles. JobPilot
          automatically selects the best match for each job.
        </p>

        {/* Role Selector */}
        <div className="mb-4">
          <label className="text-[11px] font-medium text-muted-foreground mb-1.5 block">
            Target Role
          </label>
          <Select value={roleType} onValueChange={(v) => { if (v) setRoleType(v); }}>
            <SelectTrigger className="h-9 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {roleOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value} className="text-xs">
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Upload Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            "relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all duration-200",
            dragActive
              ? "border-primary bg-primary/5"
              : "border-border hover:border-primary/50 hover:bg-muted/30"
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            hidden
            onChange={handleFileChange}
          />

          {uploading ? (
            <div className="flex flex-col items-center gap-2">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <p className="text-xs text-muted-foreground">
                Uploading and parsing resume...
              </p>
            </div>
          ) : (
            <>
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
                <Upload className="w-5 h-5 text-primary" />
              </div>
              <p className="text-xs font-medium text-foreground">
                Drop your resume here or click to browse
              </p>
              <p className="text-[10px] text-muted-foreground mt-1">
                Supports PDF and DOCX files
              </p>
            </>
          )}
        </div>

        {/* Status */}
        {status && (
          <div
            className={cn(
              "flex items-center gap-2 mt-3 px-3 py-2 rounded-lg text-xs font-medium",
              status.type === "success"
                ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                : "bg-red-50 text-red-700 border border-red-100"
            )}
          >
            {status.type === "success" ? (
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
            ) : (
              <XCircle className="w-3.5 h-3.5 shrink-0" />
            )}
            {status.message}
          </div>
        )}
      </Card>

      {/* Resume Preview */}
      {preview && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="p-5 shadow-none border">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <User className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-foreground">
                  {preview.name || "Your Profile"}
                </h3>
                <p className="text-[11px] text-muted-foreground">
                  {preview.experience_years} years experience •{" "}
                  {preview.skills_found} skills found
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <span className="text-[11px] font-medium text-foreground">
                Skills Detected
              </span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {preview.skills.slice(0, 15).map((skill) => (
                <span
                  key={skill}
                  className="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-[10px] font-medium"
                >
                  {skill}
                </span>
              ))}
              {preview.skills.length > 15 && (
                <span className="px-2 py-0.5 rounded-md bg-muted text-muted-foreground text-[10px]">
                  +{preview.skills.length - 15} more
                </span>
              )}
            </div>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}
