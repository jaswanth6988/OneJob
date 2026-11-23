"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { 
  Send, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  ExternalLink, 
  Eye, 
  FileText, 
  Camera, 
  Bot, 
  X,
  Sparkles
} from "lucide-react";
import PrivateImage from "@/components/PrivateImage";
import { api } from "@/lib/api";

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<any | null>(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<string>("ALL");

  const fetchApplications = async () => {
    setError("");
    try {
      const res = await api.applications.list(filter !== "ALL" ? filter : undefined);
      setApplications(res.data || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load applications");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, [filter]);

  // Separate polling effect — auto-refresh every 5s if any app is in progress
  useEffect(() => {
    const timer = setInterval(() => {
      setApplications(current => {
        if (current.some((a: any) => a.status === "QUEUED" || a.status === "APPLYING")) {
          fetchApplications();
        }
        return current;
      });
    }, 5000);
    return () => clearInterval(timer);
  }, [filter]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "DRY_RUN_COMPLETE": return <Badge variant="info">Dry run complete · not submitted</Badge>;
      case "SUBMITTED":
        return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5" /> Verified / Submitted</Badge>;
      case "APPLYING":
        return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 flex items-center gap-1.5 animate-pulse"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> AI Applying Now...</Badge>;
      case "QUEUED":
        return <Badge className="bg-slate-500/20 text-slate-300 border-slate-500/30 flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> In Worker Queue</Badge>;
      case "REQUIRES_MANUAL_INTERVENTION":
        return <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 flex items-center gap-1.5"><AlertTriangle className="w-3.5 h-3.5" /> Manual Action Needed</Badge>;
      case "FAILED":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30 flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const stats = {
    total: applications.length,
    submitted: applications.filter(a => a.status === "SUBMITTED").length,
    active: applications.filter(a => a.status === "QUEUED" || a.status === "APPLYING").length,
    manual: applications.filter(a => a.status === "REQUIRES_MANUAL_INTERVENTION" || a.status === "FAILED").length,
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {error && <div className="notice error" role="alert">{error}<button onClick={fetchApplications}>Retry</button></div>}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">AI Applications Tracker</h1>
          <p className="text-slate-400 mt-1">
            Monitor real-time browser auto-submissions, review visual proof screenshots, and inspect Gemini answer transcripts.
          </p>
        </div>
        <button 
          onClick={fetchApplications}
          className="flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Status
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <Card className="p-5 bg-slate-800/40 border-slate-700/60 backdrop-blur-md">
          <p className="text-sm font-medium text-slate-400">Total Tracked</p>
          <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
        </Card>
        <Card className="p-5 bg-emerald-500/10 border-emerald-500/20 backdrop-blur-md">
          <p className="text-sm font-medium text-emerald-400">Verified / Completed</p>
          <p className="text-3xl font-bold text-emerald-300 mt-1">{stats.submitted}</p>
        </Card>
        <Card className="p-5 bg-blue-500/10 border-blue-500/20 backdrop-blur-md">
          <p className="text-sm font-medium text-blue-400">In Progress</p>
          <p className="text-3xl font-bold text-blue-300 mt-1">{stats.active}</p>
        </Card>
        <Card className="p-5 bg-amber-500/10 border-amber-500/20 backdrop-blur-md">
          <p className="text-sm font-medium text-amber-400">Needs Attention</p>
          <p className="text-3xl font-bold text-amber-300 mt-1">{stats.manual}</p>
        </Card>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 pb-2 border-b border-slate-800">
        {["ALL", "SUBMITTED", "APPLYING", "QUEUED", "REQUIRES_MANUAL_INTERVENTION", "FAILED"].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
              filter === tab
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                : "bg-slate-800/60 text-slate-400 hover:bg-slate-700/60 hover:text-slate-200"
            }`}
          >
            {tab.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Main List */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="h-24 animate-pulse bg-slate-800/50 border-slate-700/50" />
          ))}
        </div>
      ) : applications.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-14 text-center border-dashed border-slate-700 bg-slate-900/40">
          <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mb-4 border border-blue-500/20">
            <Send className="w-8 h-8 text-blue-400" />
          </div>
          <h3 className="text-xl font-medium text-white mb-2">No application records found</h3>
          <p className="text-slate-400 max-w-sm mb-6">
            You have not started any AI auto-applications in this category yet. Visit the Job Discovery tab to click "1-Click AI Apply" on your top matches!
          </p>
          <a href="/jobs" className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200">
            Discover & Apply to Jobs
          </a>
        </Card>
      ) : (
        <div className="space-y-4">
          {applications.map((app) => (
            <Card key={app._id} className="p-5 bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-colors flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="space-y-2">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="font-semibold text-white text-lg tracking-tight">Application #{app._id.slice(-6)}</span>
                  {getStatusBadge(app.status)}
                  <Badge variant="outline" className="border-slate-600 bg-slate-900/80 text-slate-300 text-xs">
                    Mode: {app.mode}
                  </Badge>
                </div>
                <div className="flex items-center text-sm text-slate-400 gap-4">
                  <span>Started: {new Date(app.created_at).toLocaleString()}</span>
                  {app.apply_url && (
                    <a href={app.apply_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline flex items-center gap-1 text-xs">
                      Target URL <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setSelectedApp(app)}
                  className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-700/80 text-white hover:bg-slate-600 border border-slate-600 transition-colors flex items-center gap-2 shadow-sm"
                >
                  <Eye className="w-4 h-4 text-blue-400" />
                  Audit & Screenshots
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Auditor & Screenshots Modal */}
      {selectedApp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Bot className="w-6 h-6 text-purple-400" />
                  AI Application Auditor Reports
                </h2>
                <p className="text-sm text-slate-400">Execution traces for Application ID: {selectedApp._id}</p>
              </div>
              <button
                onClick={() => setSelectedApp(null)}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Error logs if any */}
            {selectedApp.error_log && (
              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold block">Automation Notice:</span>
                  {selectedApp.error_log}
                </div>
              </div>
            )}

            {/* Gemini Q&A Transcript Section */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2 border-l-4 border-purple-500 pl-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                Gemini AI Form Screening Answers
              </h3>
              {selectedApp.ai_answers && selectedApp.ai_answers.length > 0 ? (
                <div className="space-y-3">
                  {selectedApp.ai_answers.map((qa: any, idx: number) => (
                    <div key={idx} className="p-3.5 rounded-lg bg-slate-800/80 border border-slate-700/80 space-y-1.5">
                      <p className="text-xs font-semibold text-purple-300 uppercase tracking-wider">Form Question / Prompt:</p>
                      <p className="text-sm text-slate-200 font-medium">"{qa.question}"</p>
                      <div className="pt-2 border-t border-slate-700/50 mt-2">
                        <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">AI Generated Response Submitted:</p>
                        <p className="text-sm text-slate-300 mt-1">{qa.answer}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic bg-slate-800/30 p-3 rounded border border-slate-800">
                  No complex custom screening questions required AI interpolation on this form. Standard contact & resume details used.
                </p>
              )}
            </div>

            {/* Submitted Form Fields Table */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2 border-l-4 border-blue-500 pl-2">
                <FileText className="w-5 h-5 text-blue-400" />
                Submitted Profile & Form Data
              </h3>
              {selectedApp.submitted_fields && Object.keys(selectedApp.submitted_fields).length > 0 ? (
                <div className="overflow-x-auto rounded-lg border border-slate-800">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="bg-slate-800/90 text-slate-200 text-xs uppercase font-semibold">
                      <tr>
                        <th className="p-3 border-b border-slate-700">Field Label / Name</th>
                        <th className="p-3 border-b border-slate-700">Submitted Value</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 bg-slate-900/60">
                      {Object.entries(selectedApp.submitted_fields).map(([key, val], idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40">
                          <td className="p-3 font-medium text-slate-300">{key}</td>
                          <td className="p-3 text-slate-400 break-words max-w-md">{String(val)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic bg-slate-800/30 p-3 rounded border border-slate-800">
                  Form filling is either currently in progress or encountered an initial navigation error.
                </p>
              )}
            </div>

            {/* Verification Screenshots Carousel */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2 border-l-4 border-emerald-500 pl-2">
                <Camera className="w-5 h-5 text-emerald-400" />
                Browser Verification Screenshots
              </h3>
              {selectedApp.screenshots && selectedApp.screenshots.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedApp.screenshots.map((path: string, idx: number) => {

                    return (
                      <div key={idx} className="space-y-1 group relative">
                        <div className="border border-slate-700 rounded-lg overflow-hidden bg-black/60 aspect-video relative flex items-center justify-center">
                          <PrivateImage applicationId={selectedApp._id || selectedApp.id} index={idx}/>
                        </div>
                        <p className="text-xs text-slate-400 font-mono flex items-center justify-between px-1">
                          <span>Step {idx + 1}: {path.split(/[\/\\]/).pop()?.split('_')[2] || 'Capture'}</span>
                          <span className="text-emerald-400 font-semibold">Saved & Verified</span>
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-slate-500 italic bg-slate-800/30 p-3 rounded border border-slate-800">
                  No visual proof screenshots captured yet for this job application attempt.
                </p>
              )}
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-800">
              <button
                onClick={() => setSelectedApp(null)}
                className="px-6 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
              >
                Close Audit Modal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
