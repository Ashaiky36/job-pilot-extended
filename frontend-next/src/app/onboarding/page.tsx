"use client";

import { useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { useAuth } from "@/lib/auth";
import { uploadResume, completeOnboarding, type ResumeUploadResult } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Upload,
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Plane,
  Sparkles,
  FileText,
  User,
  Briefcase,
} from "lucide-react";

const roleOptions = [
  { value: "data_analyst", label: "Data Analyst", emoji: "📊" },
  { value: "data_scientist", label: "Data Scientist", emoji: "🧪" },
  { value: "ml_engineer", label: "ML / AI Engineer", emoji: "🤖" },
  { value: "data_engineer", label: "Data Engineer", emoji: "⚙️" },
  { value: "software_engineer", label: "Software Engineer", emoji: "💻" },
  { value: "frontend_developer", label: "Frontend Developer", emoji: "🎨" },
  { value: "backend_developer", label: "Backend Developer", emoji: "🔧" },
  { value: "fullstack_developer", label: "Fullstack Developer", emoji: "🌐" },
  { value: "devops_engineer", label: "DevOps Engineer", emoji: "☁️" },
  { value: "product_manager", label: "Product Manager", emoji: "📋" },
];

export default function OnboardingPage() {
  const { user, refreshUser } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<ResumeUploadResult | null>(null);
  const [status, setStatus] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [completing, setCompleting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const toggleRole = (role: string) => {
    setSelectedRoles((prev) =>
      prev.includes(role)
        ? prev.filter((r) => r !== role)
        : [...prev, role]
    );
  };

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".pdf") && !file.name.endsWith(".docx")) {
        setStatus({ message: "Only PDF and DOCX files are supported", type: "error" });
        return;
      }

      setUploading(true);
      setStatus(null);

      try {
        const roleType = selectedRoles[0] || "data_analyst";
        const data = await uploadResume(file, roleType);
        if (data.success) {
          setUploadResult(data);
          setStatus({ message: "Resume parsed successfully!", type: "success" });
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
    [selectedRoles]
  );

  const handleComplete = async () => {
    setCompleting(true);
    try {
      await completeOnboarding();
      await refreshUser();
      router.push("/dashboard");
    } catch (err) {
      console.error("Onboarding complete failed:", err);
    } finally {
      setCompleting(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-2.5 px-6 h-16 border-b border-slate-100 bg-white/80 backdrop-blur-sm">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
          <Plane className="w-4 h-4 text-white" />
        </div>
        <span className="text-[15px] font-bold text-slate-900 tracking-tight">
          JobPilot
        </span>
        <span className="ml-2 text-[11px] text-slate-400">
          Welcome, {user.name}!
        </span>
      </div>

      {/* Progress Bar */}
      <div className="px-6 pt-6">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center gap-3">
            <div className={cn("flex items-center gap-2", step >= 1 ? "text-indigo-600" : "text-slate-300")}>
              <div className={cn("w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold", step >= 1 ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-400")}>1</div>
              <span className="text-xs font-medium hidden sm:block">Select Roles</span>
            </div>
            <div className={cn("flex-1 h-0.5 rounded-full", step >= 2 ? "bg-indigo-600" : "bg-slate-100")} />
            <div className={cn("flex items-center gap-2", step >= 2 ? "text-indigo-600" : "text-slate-300")}>
              <div className={cn("w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold", step >= 2 ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-400")}>2</div>
              <span className="text-xs font-medium hidden sm:block">Upload Resume</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex items-start justify-center px-6 py-10">
        <div className="w-full max-w-2xl">
          {/* Step 1: Select Roles */}
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center mb-8">
                <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                  <Briefcase className="w-5 h-5 text-indigo-600" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">
                  What roles are you looking for?
                </h2>
                <p className="text-sm text-slate-500 mt-1">
                  Select one or more to help us find the best matches for you.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                {roleOptions.map((role) => {
                  const selected = selectedRoles.includes(role.value);
                  return (
                    <button
                      key={role.value}
                      onClick={() => toggleRole(role.value)}
                      className={cn(
                        "flex items-center gap-2.5 px-4 py-3 rounded-xl border text-left transition-all duration-200",
                        selected
                          ? "border-indigo-300 bg-indigo-50 shadow-sm"
                          : "border-slate-150 bg-white hover:border-slate-200 hover:shadow-sm"
                      )}
                    >
                      <span className="text-lg">{role.emoji}</span>
                      <span className={cn("text-[12px] font-medium", selected ? "text-indigo-700" : "text-slate-600")}>
                        {role.label}
                      </span>
                      {selected && <CheckCircle2 className="w-4 h-4 text-indigo-600 ml-auto shrink-0" />}
                    </button>
                  );
                })}
              </div>

              <div className="mt-8 flex justify-end">
                <Button
                  onClick={() => setStep(2)}
                  disabled={selectedRoles.length === 0}
                  className="gap-2 bg-indigo-600 hover:bg-indigo-700 text-white"
                >
                  Continue
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 2: Upload Resume */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center mb-8">
                <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-5 h-5 text-indigo-600" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">
                  Upload your resume
                </h2>
                <p className="text-sm text-slate-500 mt-1">
                  Our AI will extract your skills and experience to find the best matches.
                </p>
              </div>

              {/* Upload Zone */}
              <Card className="p-0 shadow-none border overflow-hidden">
                <div
                  onDrop={(e) => {
                    e.preventDefault();
                    setDragActive(false);
                    const file = e.dataTransfer.files[0];
                    if (file) handleUpload(file);
                  }}
                  onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                  onDragLeave={() => setDragActive(false)}
                  onClick={() => fileInputRef.current?.click()}
                  className={cn(
                    "p-10 text-center cursor-pointer transition-all duration-200",
                    dragActive
                      ? "bg-indigo-50 border-2 border-dashed border-indigo-300"
                      : "bg-white hover:bg-slate-50"
                  )}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    hidden
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleUpload(file);
                    }}
                  />

                  {uploading ? (
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
                      <p className="text-sm text-slate-500">Parsing your resume with AI...</p>
                    </div>
                  ) : (
                    <>
                      <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-6 h-6 text-indigo-500" />
                      </div>
                      <p className="text-sm font-medium text-slate-700">
                        Drop your resume here or click to browse
                      </p>
                      <p className="text-[11px] text-slate-400 mt-1">PDF or DOCX — max 10MB</p>
                    </>
                  )}
                </div>
              </Card>

              {/* Status */}
              {status && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "flex items-center gap-2 mt-4 px-4 py-2.5 rounded-lg text-xs font-medium",
                    status.type === "success"
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                      : "bg-red-50 text-red-700 border border-red-100"
                  )}
                >
                  {status.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                  {status.message}
                </motion.div>
              )}

              {/* Resume Preview */}
              {uploadResult && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className="mt-4 p-5 shadow-none border">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center">
                        <User className="w-5 h-5 text-indigo-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900">
                          {uploadResult.name || "Your Profile"}
                        </h3>
                        <p className="text-[11px] text-slate-500">
                          {uploadResult.experience_years} years experience • {uploadResult.skills_found} skills found
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 mb-2">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                      <span className="text-[11px] font-medium text-slate-700">Skills Detected</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {uploadResult.skills.slice(0, 15).map((skill) => (
                        <span
                          key={skill}
                          className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-[10px] font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                      {uploadResult.skills.length > 15 && (
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 text-[10px]">
                          +{uploadResult.skills.length - 15} more
                        </span>
                      )}
                    </div>
                  </Card>
                </motion.div>
              )}

              {/* Actions */}
              <div className="mt-8 flex items-center justify-between">
                <Button
                  variant="ghost"
                  onClick={() => setStep(1)}
                  className="text-xs text-slate-500"
                >
                  ← Back
                </Button>
                <Button
                  onClick={handleComplete}
                  disabled={completing}
                  className="gap-2 bg-indigo-600 hover:bg-indigo-700 text-white"
                >
                  {completing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      Go to Dashboard
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
