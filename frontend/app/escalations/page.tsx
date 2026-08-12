"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { UserCheck, AlertTriangle, ShieldCheck, Clock, ArrowLeft, RefreshCw, PhoneCall, HelpCircle, AlertOctagon } from "lucide-react";

interface Escalation {
  ref_id: string;
  user_id: string;
  student_name: string;
  reason: string;
  urgency: string;
  summary: string;
  user_consent: boolean;
  status: string;
  created_at: string;
}

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEscalations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/escalations");
      const data = await res.json();
      if (data.success) {
        setEscalations(data.escalations || []);
      } else {
        setError(data.error || "Failed to load escalations");
      }
    } catch (err: any) {
      setError(err?.message || "Network error loading escalations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, []);

  const totalCount = escalations.length;
  const openCount = escalations.filter((e) => e.status === "open").length;
  const highEmergencyCount = escalations.filter(
    (e) => e.urgency.toLowerCase() === "high" || e.urgency.toLowerCase() === "emergency"
  ).length;

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case "emergency":
        return <span className="px-3 py-1 rounded-md text-xs font-bold bg-red-950 text-red-400 border border-red-700/60 uppercase tracking-wider">Emergency</span>;
      case "high":
        return <span className="px-3 py-1 rounded-md text-xs font-bold bg-orange-950 text-orange-400 border border-orange-700/60 uppercase tracking-wider">High</span>;
      case "medium":
        return <span className="px-3 py-1 rounded-md text-xs font-bold bg-amber-950 text-amber-400 border border-amber-700/60 uppercase tracking-wider">Medium</span>;
      default:
        return <span className="px-3 py-1 rounded-md text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-700/60 uppercase tracking-wider">Low</span>;
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 font-sans">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Navigation & Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-neutral-800 pb-6">
          <div className="flex items-center gap-4">
            <Link href="/" className="p-2.5 rounded-xl bg-neutral-900 hover:bg-neutral-800 border border-neutral-800 text-neutral-300 hover:text-white transition">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-indigo-950 text-indigo-400 border border-indigo-800/60 text-lg">👩‍🏫</span>
                  Human Help & Escalation Desk
                </h1>
                <span className="text-xs px-3 py-1 rounded-full bg-indigo-950/80 text-indigo-400 border border-indigo-700/50 font-semibold tracking-wide">
                  Day 7 · VoiceForBharat
                </span>
              </div>
              <p className="text-xs text-neutral-400 mt-1">
                Escalation requests created by Tara when learners need human teacher assistance with explicit consent.
              </p>
            </div>
          </div>
          <button
            onClick={fetchEscalations}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold transition shadow-lg shadow-indigo-600/20 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh Desk
          </button>
        </div>

        {/* Top Summary Metric Cards (Reference UI from Video) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-neutral-900/90 border border-neutral-800 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Total Requests</p>
              <h3 className="text-3xl font-extrabold text-white mt-1">{totalCount}</h3>
            </div>
            <div className="p-3 rounded-xl bg-indigo-950 text-indigo-400 border border-indigo-800/40">
              <HelpCircle className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-neutral-900/90 border border-neutral-800 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">Open Requests</p>
              <h3 className="text-3xl font-extrabold text-indigo-400 mt-1">{openCount}</h3>
            </div>
            <div className="p-3 rounded-xl bg-indigo-950 text-indigo-400 border border-indigo-800/40">
              <Clock className="w-6 h-6" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-neutral-900/90 border border-neutral-800 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">High / Emergency</p>
              <h3 className="text-3xl font-extrabold text-red-400 mt-1">{highEmergencyCount}</h3>
            </div>
            <div className="p-3 rounded-xl bg-red-950 text-red-400 border border-red-800/40">
              <AlertOctagon className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Loading / Error states */}
        {loading && (
          <div className="text-center py-16 text-neutral-400">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-indigo-400" />
            Loading open human help requests...
          </div>
        )}

        {error && (
          <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Detailed Structured Escalation Cards */}
        {!loading && !error && (
          <div className="space-y-4">
            <div className="flex justify-between items-center text-xs font-semibold text-neutral-400 uppercase tracking-wider px-1">
              <span>Active Escalation Tickets ({escalations.length})</span>
              <span>SLA: 24–48 Hours Follow-up</span>
            </div>

            {escalations.length === 0 ? (
              <div className="text-center py-20 rounded-2xl bg-neutral-900/50 border border-neutral-800/80 p-8 space-y-4">
                <ShieldCheck className="w-14 h-14 text-emerald-400 mx-auto" />
                <h3 className="text-xl font-bold text-white">No Open Help Requests</h3>
                <p className="text-sm text-neutral-400 max-w-md mx-auto">
                  Tara is successfully handling all reading sessions! Requests will appear here whenever a student requests human teacher assistance with explicit consent.
                </p>
              </div>
            ) : (
              <div className="grid gap-6">
                {escalations.map((item) => (
                  <div
                    key={item.ref_id}
                    className="p-6 rounded-2xl bg-neutral-900/90 border border-neutral-800 hover:border-indigo-900/60 transition shadow-xl space-y-5"
                  >
                    {/* Ticket Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-800/80 pb-4">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-sm font-black text-indigo-400 bg-indigo-950/80 px-3 py-1.5 rounded-lg border border-indigo-800/60 tracking-wider">
                          {item.ref_id}
                        </span>
                        {getUrgencyBadge(item.urgency)}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs px-3 py-1 rounded-md font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800/50 flex items-center gap-1.5">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Consent Granted ✓
                        </span>
                        <span className="text-xs px-3 py-1 rounded-md font-semibold bg-neutral-800 text-neutral-300 border border-neutral-700">
                          Status: Open
                        </span>
                      </div>
                    </div>

                    {/* Reference Grid Detail Cards (From Video Format) */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Who needs help */}
                      <div className="p-4 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500">Who Needs Help</span>
                        <p className="text-sm font-semibold text-white flex items-center gap-2">
                          <UserCheck className="w-4 h-4 text-indigo-400" />
                          {item.student_name} <span className="text-xs text-neutral-400">({item.user_id})</span>
                        </p>
                      </div>

                      {/* What happened */}
                      <div className="p-4 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500">What Happened</span>
                        <p className="text-sm font-medium text-neutral-200 capitalize">
                          {item.reason.replace(/_/g, " ")}
                        </p>
                      </div>

                      {/* Summary */}
                      <div className="p-4 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-1 md:col-span-2">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500">Agent Summary & Context</span>
                        <p className="text-xs text-neutral-300 leading-relaxed font-mono bg-neutral-900/60 p-3 rounded-lg border border-neutral-850">
                          {item.summary}
                        </p>
                      </div>

                      {/* Language */}
                      <div className="p-4 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500">Language</span>
                        <p className="text-sm font-semibold text-emerald-400">Hinglish / Devanagari Script</p>
                      </div>

                      {/* Preferred follow up */}
                      <div className="p-4 rounded-xl bg-neutral-950/70 border border-neutral-800/80 space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-neutral-500">Preferred Follow Up</span>
                        <p className="text-sm font-semibold text-indigo-400 flex items-center gap-2">
                          <PhoneCall className="w-4 h-4" />
                          Voice Practice Callback
                        </p>
                      </div>
                    </div>

                    {/* Footer timestamp */}
                    <div className="flex justify-between items-center text-xs text-neutral-500 pt-2 border-t border-neutral-800/50">
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>Created: {new Date(item.created_at).toLocaleString()}</span>
                      </div>
                      <span className="text-xs font-semibold text-indigo-400">
                        VoiceForBharat Teacher Queue
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
