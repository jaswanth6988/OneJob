"use client";

import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  Bot, Sparkles, Briefcase, MessageSquare, ChevronRight,
  Send, Loader2, CheckCircle, XCircle, AlertCircle, Target,
  TrendingUp, Star, RefreshCw, User, Lightbulb, Award
} from "lucide-react";

type Tab = "tailor" | "interview" | "chat";

interface ChatMsg { role: "user" | "assistant"; content: string; }

// ---------- Tailor Tab ----------
function ResumeTailorTab() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    api.get<any>("/jobs?page_size=50").then(r => setJobs(r.data?.items || [])).catch(() => {});
  }, []);

  const run = async () => {
    if (!selectedJobId) return;
    setLoading(true); setAnalysis(null);
    try {
      const res = await api.tailor.analyze(selectedJobId);
      setAnalysis(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const score = analysis?.tailored_ats_score ?? 0;
  const current = analysis?.current_ats_score ?? 0;
  const gain = score - current;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-3">
        <select
          value={selectedJobId}
          onChange={e => setSelectedJobId(e.target.value)}
          className="flex-1 px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a job to tailor your resume for...</option>
          {jobs.map(j => (
            <option key={j._id} value={j._id}>{j.title} — {j.company}</option>
          ))}
        </select>
        <button
          onClick={run}
          disabled={!selectedJobId || loading}
          className="flex items-center px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold text-sm hover:shadow-lg hover:shadow-blue-500/25 transition-all disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
          {loading ? "Analyzing..." : "AI Tailor My Resume"}
        </button>
      </div>

      {loading && (
        <Card className="p-10 flex flex-col items-center justify-center border-slate-700 bg-slate-900/60">
          <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center mb-4 border border-blue-500/20 animate-pulse">
            <Sparkles className="w-8 h-8 text-blue-400" />
          </div>
          <p className="text-slate-300 font-medium">Gemini is analyzing your resume against the job description...</p>
          <p className="text-slate-500 text-sm mt-1">This takes 10–20 seconds</p>
        </Card>
      )}

      {analysis && (
        <div className="space-y-5 animate-in fade-in slide-in-from-bottom-3 duration-400">
          {/* ATS Score Banner */}
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5 bg-slate-800/60 border-slate-700 text-center">
              <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Current ATS Score</p>
              <p className="text-4xl font-bold text-red-400">{current}%</p>
            </Card>
            <Card className={`p-5 text-center border ${gain >= 0 ? 'bg-emerald-500/10 border-emerald-500/25' : 'bg-slate-800/60 border-slate-700'}`}>
              <p className="text-xs font-semibold text-emerald-400 uppercase mb-1">Score After Tailoring</p>
              <p className="text-4xl font-bold text-emerald-400">{score}%</p>
            </Card>
            <Card className="p-5 bg-blue-500/10 border-blue-500/25 text-center">
              <p className="text-xs font-semibold text-blue-400 uppercase mb-1">AI Improvement</p>
              <p className="text-4xl font-bold text-blue-400">+{gain}%</p>
            </Card>
          </div>

          {/* Summary Rewrite */}
          <Card className="p-5 border-slate-700 bg-slate-900/60">
            <h3 className="text-sm font-bold text-purple-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Star className="w-4 h-4" /> AI-Rewritten Professional Summary
            </h3>
            <p className="text-slate-200 leading-relaxed text-sm bg-slate-800/50 p-4 rounded-lg border border-slate-700 italic">
              "{analysis.summary_rewrite}"
            </p>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Skills to Highlight */}
            {analysis.skills_to_highlight?.length > 0 && (
              <Card className="p-5 border-emerald-500/20 bg-emerald-500/5">
                <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" /> Prioritize These Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.skills_to_highlight.map((s: string, i: number) => (
                    <Badge key={i} className="bg-emerald-500/15 text-emerald-300 border-emerald-500/30">{s}</Badge>
                  ))}
                </div>
              </Card>
            )}

            {/* Skills to Add */}
            {analysis.skills_to_add?.length > 0 && (
              <Card className="p-5 border-amber-500/20 bg-amber-500/5">
                <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4" /> Skills to Add / Learn
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysis.skills_to_add.map((s: string, i: number) => (
                    <Badge key={i} className="bg-amber-500/15 text-amber-300 border-amber-500/30">{s}</Badge>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* ATS Keyword Gaps */}
          {analysis.keyword_gaps?.length > 0 && (
            <Card className="p-5 border-red-500/20 bg-red-500/5">
              <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <XCircle className="w-4 h-4" /> Missing ATS Keywords (Add to Resume)
              </h3>
              <div className="flex flex-wrap gap-2">
                {analysis.keyword_gaps.map((kw: string, i: number) => (
                  <Badge key={i} className="bg-red-500/15 text-red-300 border-red-500/30 font-mono text-xs">{kw}</Badge>
                ))}
              </div>
            </Card>
          )}

          {/* Bullet Improvements */}
          {analysis.bullet_improvements?.length > 0 && (
            <Card className="p-5 border-slate-700 bg-slate-900/60 space-y-4">
              <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
                <Lightbulb className="w-4 h-4" /> Experience Bullet Point Improvements
              </h3>
              {analysis.bullet_improvements.map((b: any, i: number) => (
                <div key={i} className="space-y-2 pb-4 border-b border-slate-800 last:border-0 last:pb-0">
                  <div className="flex items-start gap-2">
                    <XCircle className="w-3.5 h-3.5 text-red-400 mt-1 shrink-0" />
                    <p className="text-sm text-slate-400 line-through">{b.original}</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-1 shrink-0" />
                    <p className="text-sm text-emerald-300">{b.improved}</p>
                  </div>
                </div>
              ))}
            </Card>
          )}

          {/* Overall Advice */}
          {analysis.overall_advice && (
            <Card className="p-5 border-purple-500/20 bg-purple-500/5">
              <h3 className="text-sm font-bold text-purple-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                <Bot className="w-4 h-4" /> Coach's Strategic Advice
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">{analysis.overall_advice}</p>
            </Card>
          )}
        </div>
      )}

      {!analysis && !loading && (
        <Card className="p-12 flex flex-col items-center text-center border-dashed border-slate-700 bg-slate-900/40">
          <div className="w-14 h-14 rounded-full bg-blue-500/10 flex items-center justify-center mb-4 border border-blue-500/20">
            <Target className="w-7 h-7 text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Tailor Your Resume with AI</h3>
          <p className="text-slate-400 text-sm max-w-md">
            Select any discovered job above. Gemini will analyze your resume against that job description and provide a detailed ATS score, keyword gaps, rewritten summary, and bullet point improvements.
          </p>
        </Card>
      )}
    </div>
  );
}

// ---------- Interview Prep Tab ----------
function InterviewPrepTab() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [questions, setQuestions] = useState<any[]>([]);
  const [loadingQ, setLoadingQ] = useState(false);
  const [activeQ, setActiveQ] = useState<any | null>(null);
  const [answer, setAnswer] = useState("");
  const [evaluating, setEvaluating] = useState(false);
  const [evaluation, setEvaluation] = useState<any | null>(null);

  useEffect(() => {
    api.get<any>("/jobs?page_size=50").then(r => setJobs(r.data?.items || [])).catch(() => {});
  }, []);

  const generateQuestions = async () => {
    if (!selectedJobId) return;
    setLoadingQ(true); setQuestions([]); setActiveQ(null); setEvaluation(null);
    try {
      const res = await api.interview.generateQuestions(selectedJobId);
      setQuestions(res.data || []);
    } catch (e) { console.error(e); }
    finally { setLoadingQ(false); }
  };

  const evaluate = async () => {
    if (!activeQ || !answer.trim()) return;
    setEvaluating(true); setEvaluation(null);
    try {
      const res = await api.interview.evaluateAnswer(selectedJobId, activeQ.question, answer);
      setEvaluation(res.data);
    } catch (e) { console.error(e); }
    finally { setEvaluating(false); }
  };

  const typeColors: Record<string, string> = {
    behavioral: "bg-blue-500/15 text-blue-300 border-blue-500/30",
    technical: "bg-purple-500/15 text-purple-300 border-purple-500/30",
    culture_fit: "bg-teal-500/15 text-teal-300 border-teal-500/30",
  };
  const diffColors: Record<string, string> = {
    easy: "text-emerald-400", medium: "text-amber-400", hard: "text-red-400"
  };

  const verdictColor = (v: string) => {
    if (v === "Excellent") return "text-emerald-400 bg-emerald-500/10 border-emerald-500/25";
    if (v === "Good") return "text-blue-400 bg-blue-500/10 border-blue-500/25";
    if (v === "Needs Improvement") return "text-amber-400 bg-amber-500/10 border-amber-500/25";
    return "text-red-400 bg-red-500/10 border-red-500/25";
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row gap-3">
        <select
          value={selectedJobId}
          onChange={e => setSelectedJobId(e.target.value)}
          className="flex-1 px-3 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="">Select a job for interview practice...</option>
          {jobs.map(j => (
            <option key={j._id} value={j._id}>{j.title} — {j.company}</option>
          ))}
        </select>
        <button
          onClick={generateQuestions}
          disabled={!selectedJobId || loadingQ}
          className="flex items-center px-5 py-2.5 rounded-lg bg-gradient-to-r from-teal-600 to-blue-600 text-white font-semibold text-sm hover:shadow-lg transition-all disabled:opacity-50"
        >
          {loadingQ ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}
          {loadingQ ? "Generating..." : "Generate Questions"}
        </button>
      </div>

      {questions.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Question Bank */}
          <div className="space-y-3">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Question Bank ({questions.length})</p>
            {questions.map((q) => (
              <button
                key={q.id}
                onClick={() => { setActiveQ(q); setAnswer(""); setEvaluation(null); }}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-150 ${activeQ?.id === q.id ? 'bg-blue-600/20 border-blue-500/50' : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'}`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Badge className={`text-xs ${typeColors[q.type] || ''}`}>{q.type.replace("_", " ")}</Badge>
                  <span className={`text-xs font-semibold ${diffColors[q.difficulty] || 'text-slate-400'}`}>● {q.difficulty}</span>
                  <span className="text-xs text-slate-500 ml-auto">{q.focus_area}</span>
                </div>
                <p className="text-sm text-slate-200 leading-snug line-clamp-2">{q.question}</p>
              </button>
            ))}
          </div>

          {/* Answer & Feedback Panel */}
          <div className="space-y-4">
            {activeQ ? (
              <>
                <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700">
                  <div className="flex items-center gap-2 mb-3">
                    <Badge className={`text-xs ${typeColors[activeQ.type] || ''}`}>{activeQ.type.replace("_", " ")}</Badge>
                    <span className={`text-xs font-bold ${diffColors[activeQ.difficulty] || ''}`}>{activeQ.difficulty}</span>
                  </div>
                  <p className="text-white font-medium leading-snug">{activeQ.question}</p>
                </div>

                <textarea
                  value={answer}
                  onChange={e => setAnswer(e.target.value)}
                  placeholder="Type your answer here... (aim for 2-4 sentences using the STAR method for behavioral questions)"
                  rows={5}
                  className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500 resize-none"
                />
                <button
                  onClick={evaluate}
                  disabled={!answer.trim() || evaluating}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold text-sm hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {evaluating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Award className="w-4 h-4" />}
                  {evaluating ? "AI is evaluating your answer..." : "Submit for AI Feedback"}
                </button>

                {evaluation && (
                  <div className="space-y-4 animate-in fade-in duration-300">
                    {/* Score */}
                    <div className={`flex items-center justify-between p-4 rounded-xl border ${verdictColor(evaluation.verdict)}`}>
                      <div>
                        <p className="text-xs font-bold uppercase tracking-wider opacity-70">AI Verdict</p>
                        <p className="text-xl font-bold">{evaluation.verdict}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs opacity-70 uppercase">Score</p>
                        <p className="text-3xl font-bold">{evaluation.score}<span className="text-base">/100</span></p>
                      </div>
                    </div>

                    {evaluation.strengths?.length > 0 && (
                      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
                        <p className="text-xs font-bold text-emerald-400 uppercase">Strengths</p>
                        {evaluation.strengths.map((s: string, i: number) => (
                          <div key={i} className="flex items-start gap-2"><CheckCircle className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" /><p className="text-sm text-slate-300">{s}</p></div>
                        ))}
                      </div>
                    )}

                    {evaluation.improvements?.length > 0 && (
                      <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-2">
                        <p className="text-xs font-bold text-amber-400 uppercase">Improvements</p>
                        {evaluation.improvements.map((imp: string, i: number) => (
                          <div key={i} className="flex items-start gap-2"><AlertCircle className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" /><p className="text-sm text-slate-300">{imp}</p></div>
                        ))}
                      </div>
                    )}

                    <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
                      <p className="text-xs font-bold text-blue-400 uppercase mb-2">Model Answer</p>
                      <p className="text-sm text-slate-300 leading-relaxed italic">"{evaluation.model_answer}"</p>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <Card className="p-8 flex flex-col items-center text-center border-dashed border-slate-700 bg-slate-900/40 h-full justify-center">
                <MessageSquare className="w-10 h-10 text-slate-600 mb-3" />
                <p className="text-slate-400 text-sm">Click any question on the left to start practicing</p>
              </Card>
            )}
          </div>
        </div>
      )}

      {!loadingQ && questions.length === 0 && (
        <Card className="p-12 flex flex-col items-center text-center border-dashed border-slate-700 bg-slate-900/40">
          <div className="w-14 h-14 rounded-full bg-teal-500/10 flex items-center justify-center mb-4 border border-teal-500/20">
            <MessageSquare className="w-7 h-7 text-teal-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">AI Interview Coach</h3>
          <p className="text-slate-400 text-sm max-w-md">
            Select a job above and generate a custom question bank. Then practice answering questions and get instant AI-scored feedback with a model ideal answer.
          </p>
        </Card>
      )}
    </div>
  );
}

// ---------- Chat Tab ----------
function ChatTab() {
  const [messages, setMessages] = useState<ChatMsg[]>([
    { role: "assistant", content: "Hi! I'm your AI career coach. I have context about your resume and discovered jobs. Ask me anything — resume tips, interview strategies, salary negotiation, or career advice!" }
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    const newMessages: ChatMsg[] = [...messages, { role: "user", content: text }];
    setMessages(newMessages);
    setSending(true);
    try {
      const history = newMessages.slice(0, -1).map(m => ({ role: m.role, content: m.content }));
      const res = await api.chat.send(text, history);
      const reply = res.data?.reply || "I'm having trouble responding right now. Please try again.";
      setMessages(prev => [...prev, { role: "assistant", content: reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: "assistant", content: "Connection error. Please check your backend is running and try again." }]);
    } finally {
      setSending(false);
    }
  };

  const quickPrompts = [
    "How do I improve my resume for a senior role?",
    "What are the top 3 things to do before a technical interview?",
    "How should I negotiate my salary?",
    "Write me a cover letter opening for a software engineering role",
  ];

  return (
    <div className="flex flex-col h-[580px]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4 pr-1 scroll-smooth">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "assistant" ? "bg-purple-500/20 border border-purple-500/30" : "bg-blue-600"}`}>
              {msg.role === "assistant" ? <Bot className="w-4 h-4 text-purple-400" /> : <User className="w-4 h-4 text-white" />}
            </div>
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
              msg.role === "assistant"
                ? "bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700"
                : "bg-blue-600 text-white rounded-tr-none"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center bg-purple-500/20 border border-purple-500/30">
              <Bot className="w-4 h-4 text-purple-400" />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-slate-800 border border-slate-700">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick Prompts */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 py-3 border-t border-slate-800">
          {quickPrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => setInput(p)}
              className="px-3 py-1.5 text-xs text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 rounded-full transition-colors"
            >
              {p}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-3 pt-3 border-t border-slate-800">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="Ask your AI career coach anything..."
          className="flex-1 px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
        <button
          onClick={send}
          disabled={!input.trim() || sending}
          className="w-12 h-12 flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:shadow-lg transition-all disabled:opacity-40"
        >
          {sending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </div>
    </div>
  );
}

// ---------- Main Page ----------
export default function AssistantPage() {
  const [tab, setTab] = useState<Tab>("tailor");

  const tabs: { id: Tab; label: string; icon: any; desc: string; gradient: string }[] = [
    { id: "tailor", label: "Resume Tailor", icon: Sparkles, desc: "AI rewrites & ATS score", gradient: "from-blue-500 to-purple-500" },
    { id: "interview", label: "Interview Prep", icon: Briefcase, desc: "Practice & get AI feedback", gradient: "from-teal-500 to-blue-500" },
    { id: "chat", label: "AI Career Chat", icon: MessageSquare, desc: "Ask your career coach", gradient: "from-purple-500 to-pink-500" },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Bot className="w-8 h-8 text-purple-400" />
          AI Career Assistant Hub
        </h1>
        <p className="text-slate-400 mt-1">
          Tailor your resume for any job, practice interviews with live AI scoring, and chat with your personal career coach.
        </p>
      </div>

      {/* Tab Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {tabs.map(t => {
          const Icon = t.icon;
          const active = tab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`p-4 rounded-xl border text-left transition-all duration-200 ${
                active
                  ? `bg-gradient-to-br ${t.gradient} bg-opacity-20 border-transparent shadow-lg`
                  : "bg-slate-800/50 border-slate-700 hover:border-slate-500 hover:bg-slate-800"
              }`}
            >
              <div className="flex items-center gap-3 mb-1">
                <Icon className={`w-5 h-5 ${active ? "text-white" : "text-slate-400"}`} />
                <span className={`font-semibold text-sm ${active ? "text-white" : "text-slate-300"}`}>{t.label}</span>
                {active && <ChevronRight className="w-4 h-4 text-white ml-auto" />}
              </div>
              <p className={`text-xs ${active ? "text-white/70" : "text-slate-500"}`}>{t.desc}</p>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <Card className="p-6 bg-slate-900/50 border-slate-700/60">
        {tab === "tailor" && <ResumeTailorTab />}
        {tab === "interview" && <InterviewPrepTab />}
        {tab === "chat" && <ChatTab />}
      </Card>
    </div>
  );
}
