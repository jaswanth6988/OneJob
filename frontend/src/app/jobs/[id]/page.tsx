"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ArrowLeft, Building, MapPin, Globe, Sparkles, ExternalLink, Clock, CheckCircle2, XCircle } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await api.get(`/jobs/${params.id}`);
        setJob(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    if (params.id) {
      fetchJob();
    }
  }, [params.id]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 w-1/3 bg-slate-800 rounded"></div>
        <div className="h-64 bg-slate-800/50 rounded-xl"></div>
      </div>
    );
  }

  if (!job) {
    return <div>Job not found</div>;
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 60) return "text-yellow-400";
    if (score > 0) return "text-red-400";
    return "text-slate-400";
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-5xl mx-auto">
      <button 
        onClick={() => router.back()}
        className="flex items-center text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Jobs
      </button>

      {/* Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 blur-3xl rounded-full -mr-32 -mt-32 pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-white">{job.title}</h1>
              <div className="flex flex-wrap items-center gap-4 text-slate-400 text-sm">
                <span className="flex items-center">
                  <Building className="w-4 h-4 mr-1.5" />
                  {job.company}
                </span>
                {job.location && (
                  <span className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1.5" />
                    {job.location}
                  </span>
                )}
                <span className="flex items-center">
                  <Globe className="w-4 h-4 mr-1.5" />
                  {job.remote_type}
                </span>
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1.5" />
                  {new Date(job.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="bg-slate-800 text-slate-300">
                {job.source_name}
              </Badge>
              {job.salary_range && (
                <Badge variant="outline" className="text-green-400 border-green-400/30">
                  {job.salary_range}
                </Badge>
              )}
              <Badge variant="outline" className="text-blue-400 border-blue-400/30">
                {job.status}
              </Badge>
            </div>
          </div>

          <div className="flex flex-col gap-3 min-w-[200px]">
            <a 
              href={job.apply_url || job.url} 
              target="_blank" 
              rel="noreferrer"
              className="flex items-center justify-center w-full px-4 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-500 transition-colors"
            >
              Apply Now
              <ExternalLink className="w-4 h-4 ml-2" />
            </a>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          <section className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
            <h2 className="text-xl font-semibold text-white mb-6">Job Description</h2>
            <div 
              className="prose prose-invert max-w-none text-slate-300 prose-a:text-blue-400 prose-headings:text-white"
              dangerouslySetInnerHTML={{ __html: job.description.replace(/\n/g, '<br/>') }}
            />
          </section>
        </div>

        {/* AI Analysis Sidebar */}
        <div className="space-y-6">
          <Card className="bg-gradient-to-b from-slate-800/50 to-slate-900 border-slate-700 p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
              <Sparkles className="w-24 h-24" />
            </div>
            
            <h3 className="flex items-center text-lg font-semibold text-white mb-6">
              <Sparkles className="w-5 h-5 mr-2 text-blue-400" />
              AI Match Analysis
            </h3>
            
            {job.score > 0 ? (
              <div className="space-y-6">
                <div className="text-center pb-6 border-b border-slate-700">
                  <div className={`text-5xl font-bold mb-2 ${getScoreColor(job.score)}`}>
                    {Math.round(job.score)}%
                  </div>
                  <p className="text-sm text-slate-400 font-medium">Match Score</p>
                </div>

                {job.match_result?.reason && (
                  <div className="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                    "{job.match_result.reason}"
                  </div>
                )}

                {job.match_result?.matched_skills?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-emerald-400 mb-3 flex items-center">
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      Matched Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {job.match_result.matched_skills.map((skill: string, i: number) => (
                        <Badge key={i} variant="outline" className="bg-emerald-400/10 text-emerald-400 border-emerald-400/20">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {job.match_result?.missing_skills?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-red-400 mb-3 flex items-center">
                      <XCircle className="w-4 h-4 mr-2" />
                      Missing Skills
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {job.match_result.missing_skills.map((skill: string, i: number) => (
                        <Badge key={i} variant="outline" className="bg-red-400/10 text-red-400 border-red-400/20">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-400 text-sm mb-4">This job hasn't been scored by the AI yet.</p>
                <button className="px-4 py-2 text-sm rounded-lg bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 transition-colors">
                  Run Analysis
                </button>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
