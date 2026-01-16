"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle, Clock, FileText, Play, XCircle } from "lucide-react";

// Types
interface Job {
  id: number;
  title: str;
  company: str;
  url: str;
  status: str; // "discovered", "tailored", "applied", "rejected"
  fit_score: number;
  created_at: string;
}

interface Stats {
  total_jobs: number;
  apps_submitted: number;
  pending_approval: number;
}

const API_BASE = "http://localhost:8000/api";

export default function Dashboard() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats>({ total_jobs: 0, apps_submitted: 0, pending_approval: 0 });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [jobsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/jobs?limit=50`),
        fetch(`${API_BASE}/stats`)
      ]);

      if (jobsRes.ok) setJobs(await jobsRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (jobId: number) => {
    try {
      await fetch(`${API_BASE}/applications/${jobId}/approve`, { method: "POST" });
      fetchData(); // Refresh immediately
    } catch (e) {
      console.error(e);
    }
  };

  const handleReject = async (jobId: number) => {
    try {
      await fetch(`${API_BASE}/applications/${jobId}/reject`, { method: "POST" });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AAJAS Command Center
          </h1>
          <p className="text-neutral-400">Agentic Autonomous Job Application System</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          <span className="text-sm text-green-400 font-medium">System Online</span>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KpiCard
          icon={<FileText className="w-8 h-8 text-blue-400" />}
          label="Total Jobs Found"
          value={stats.total_jobs}
          color="border-blue-500/20 bg-blue-500/10"
        />
        <KpiCard
          icon={<Clock className="w-8 h-8 text-amber-400" />}
          label="Pending Approval"
          value={stats.pending_approval}
          color="border-amber-500/20 bg-amber-500/10"
        />
        <KpiCard
          icon={<CheckCircle className="w-8 h-8 text-green-400" />}
          label="Applications Submitted"
          value={stats.apps_submitted}
          color="border-green-500/20 bg-green-500/10"
        />
      </div>

      {/* Main Content */}
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Job Queue/Activity */}
        <div className="lg:col-span-2 bg-neutral-900/50 border border-neutral-800 rounded-xl p-6 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-400" />
              Live Activity Queue
            </h2>
            <span className="text-xs text-neutral-500">Auto-refreshing...</span>
          </div>

          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-10 text-neutral-500">Loading neural link...</div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-10 text-neutral-500">No jobs in queue. Start the Scout Agent.</div>
            ) : (
              jobs.map((job) => (
                <div key={job.id} className="group relative bg-neutral-900 border border-neutral-800 hover:border-neutral-700 p-4 rounded-lg transition-all">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-lg text-neutral-200 group-hover:text-white">{job.title}</h3>
                      <p className="text-neutral-400 text-sm">{job.company}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <Badge status={job.status} />
                        <span className="text-xs text-neutral-500">Fit Score: {job.fit_score}%</span>
                      </div>
                    </div>

                    {/* Actions */}
                    {job.status === "tailored" || job.status === "discovered" ? ( // Assuming Pending logic usually maps to tailored/ready
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleReject(job.id)}
                          className="p-2 rounded-full hover:bg-red-500/20 text-neutral-400 hover:text-red-400 transition-colors"
                          title="Reject"
                        >
                          <XCircle className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleApprove(job.id)}
                          className="px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-md text-sm font-medium flex items-center gap-2 transition-colors shadow-lg shadow-green-900/20"
                        >
                          <Play className="w-4 h-4" /> Approve
                        </button>
                      </div>
                    ) : null}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Sidebar / Logs */}
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-6 text-neutral-300">System Logs</h2>
          <div className="space-y-3 font-mono text-xs text-neutral-400">
            <div className="p-3 bg-black/40 rounded border border-neutral-800">
              <span className="text-green-400">[12:00:01]</span> System initialized.
            </div>
            <div className="p-3 bg-black/40 rounded border border-neutral-800">
              <span className="text-blue-400">[12:00:05]</span> Scout Agent active.
            </div>
            {/* We could fetch real logs here later */}
            <div className="p-3 bg-black/40 rounded border border-neutral-800 opacity-50">
              Waiting for events...
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Components
function KpiCard({ icon, label, value, color }: { icon: any, label: string, value: number, color: string }) {
  return (
    <div className={`p-6 rounded-xl border ${color} relative overflow-hidden`}>
      <div className="flex justify-between items-start z-10 relative">
        <div>
          <p className="text-neutral-400 text-sm font-medium mb-1">{label}</p>
          <h3 className="text-3xl font-bold text-white">{value}</h3>
        </div>
        {icon}
      </div>
    </div>
  );
}

function Badge({ status }: { status: string }) {
  const styles = {
    discovered: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    tailored: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    applied: "bg-green-500/10 text-green-400 border-green-500/20",
    rejected: "bg-red-500/10 text-red-400 border-red-500/20",
  };
  const style = styles[status as keyof typeof styles] || "bg-gray-500/10 text-gray-400";

  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${style} capitalize`}>
      {status}
    </span>
  );
}
