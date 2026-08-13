'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  AlertOctagon,
  AlertTriangle,
  ArrowLeft,
  Clock,
  HelpCircle,
  PhoneCall,
  RefreshCw,
  ShieldCheck,
  UserCheck,
} from 'lucide-react';

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
      const res = await fetch('/api/escalations');
      const data = await res.json();
      if (data.success) {
        setEscalations(data.escalations || []);
      } else {
        setError(data.error || 'Failed to load escalations');
      }
    } catch (err: any) {
      setError(err?.message || 'Network error loading escalations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, []);

  const totalCount = escalations.length;
  const openCount = escalations.filter((e) => e.status === 'open').length;
  const highEmergencyCount = escalations.filter(
    (e) => e.urgency.toLowerCase() === 'high' || e.urgency.toLowerCase() === 'emergency'
  ).length;

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'emergency':
        return (
          <span className="rounded-md border border-red-700/60 bg-red-950 px-3 py-1 text-xs font-bold tracking-wider text-red-400 uppercase">
            Emergency
          </span>
        );
      case 'high':
        return (
          <span className="rounded-md border border-orange-700/60 bg-orange-950 px-3 py-1 text-xs font-bold tracking-wider text-orange-400 uppercase">
            High
          </span>
        );
      case 'medium':
        return (
          <span className="rounded-md border border-amber-700/60 bg-amber-950 px-3 py-1 text-xs font-bold tracking-wider text-amber-400 uppercase">
            Medium
          </span>
        );
      default:
        return (
          <span className="rounded-md border border-emerald-700/60 bg-emerald-950 px-3 py-1 text-xs font-bold tracking-wider text-emerald-400 uppercase">
            Low
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 p-6 font-sans text-neutral-100 md:p-10">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* Navigation & Header */}
        <div className="flex flex-col items-start justify-between gap-4 border-b border-neutral-800 pb-6 md:flex-row md:items-center">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="rounded-xl border border-neutral-800 bg-neutral-900 p-2.5 text-neutral-300 transition hover:bg-neutral-800 hover:text-white"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight text-white">
                  <span className="rounded-lg border border-indigo-800/60 bg-indigo-950 p-1.5 text-lg text-indigo-400">
                    👩‍🏫
                  </span>
                  Human Help & Escalation Desk
                </h1>
                <span className="rounded-full border border-indigo-700/50 bg-indigo-950/80 px-3 py-1 text-xs font-semibold tracking-wide text-indigo-400">
                  Day 7 · VoiceForBharat
                </span>
              </div>
              <p className="mt-1 text-xs text-neutral-400">
                Escalation requests created by Tara when learners need human teacher assistance with
                explicit consent.
              </p>
            </div>
          </div>
          <button
            onClick={fetchEscalations}
            disabled={loading}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-500 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Desk
          </button>
        </div>

        {/* Top Summary Metric Cards (Reference UI from Video) */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="flex items-center justify-between rounded-2xl border border-neutral-800 bg-neutral-900/90 p-5">
            <div>
              <p className="text-xs font-semibold tracking-wider text-neutral-400 uppercase">
                Total Requests
              </p>
              <h3 className="mt-1 text-3xl font-extrabold text-white">{totalCount}</h3>
            </div>
            <div className="rounded-xl border border-indigo-800/40 bg-indigo-950 p-3 text-indigo-400">
              <HelpCircle className="h-6 w-6" />
            </div>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-neutral-800 bg-neutral-900/90 p-5">
            <div>
              <p className="text-xs font-semibold tracking-wider text-neutral-400 uppercase">
                Open Requests
              </p>
              <h3 className="mt-1 text-3xl font-extrabold text-indigo-400">{openCount}</h3>
            </div>
            <div className="rounded-xl border border-indigo-800/40 bg-indigo-950 p-3 text-indigo-400">
              <Clock className="h-6 w-6" />
            </div>
          </div>

          <div className="flex items-center justify-between rounded-2xl border border-neutral-800 bg-neutral-900/90 p-5">
            <div>
              <p className="text-xs font-semibold tracking-wider text-neutral-400 uppercase">
                High / Emergency
              </p>
              <h3 className="mt-1 text-3xl font-extrabold text-red-400">{highEmergencyCount}</h3>
            </div>
            <div className="rounded-xl border border-red-800/40 bg-red-950 p-3 text-red-400">
              <AlertOctagon className="h-6 w-6" />
            </div>
          </div>
        </div>

        {/* Loading / Error states */}
        {loading && (
          <div className="py-16 text-center text-neutral-400">
            <RefreshCw className="mx-auto mb-3 h-8 w-8 animate-spin text-indigo-400" />
            Loading open human help requests...
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 rounded-xl border border-red-800 bg-red-950/40 p-4 text-sm text-red-300">
            <AlertTriangle className="h-5 w-5 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Detailed Structured Escalation Cards */}
        {!loading && !error && (
          <div className="space-y-4">
            <div className="flex items-center justify-between px-1 text-xs font-semibold tracking-wider text-neutral-400 uppercase">
              <span>Active Escalation Tickets ({escalations.length})</span>
              <span>SLA: 24–48 Hours Follow-up</span>
            </div>

            {escalations.length === 0 ? (
              <div className="space-y-4 rounded-2xl border border-neutral-800/80 bg-neutral-900/50 p-8 py-20 text-center">
                <ShieldCheck className="mx-auto h-14 w-14 text-emerald-400" />
                <h3 className="text-xl font-bold text-white">No Open Help Requests</h3>
                <p className="mx-auto max-w-md text-sm text-neutral-400">
                  Tara is successfully handling all reading sessions! Requests will appear here
                  whenever a student requests human teacher assistance with explicit consent.
                </p>
              </div>
            ) : (
              <div className="grid gap-6">
                {escalations.map((item) => (
                  <div
                    key={item.ref_id}
                    className="space-y-5 rounded-2xl border border-neutral-800 bg-neutral-900/90 p-6 shadow-xl transition hover:border-indigo-900/60"
                  >
                    {/* Ticket Header */}
                    <div className="flex flex-col justify-between gap-3 border-b border-neutral-800/80 pb-4 sm:flex-row sm:items-center">
                      <div className="flex items-center gap-3">
                        <span className="rounded-lg border border-indigo-800/60 bg-indigo-950/80 px-3 py-1.5 font-mono text-sm font-black tracking-wider text-indigo-400">
                          {item.ref_id}
                        </span>
                        {getUrgencyBadge(item.urgency)}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1.5 rounded-md border border-emerald-800/50 bg-emerald-950 px-3 py-1 text-xs font-semibold text-emerald-300">
                          <ShieldCheck className="h-3.5 w-3.5" />
                          Consent Granted ✓
                        </span>
                        <span className="rounded-md border border-neutral-700 bg-neutral-800 px-3 py-1 text-xs font-semibold text-neutral-300">
                          Status: Open
                        </span>
                      </div>
                    </div>

                    {/* Reference Grid Detail Cards (From Video Format) */}
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                      {/* Who needs help */}
                      <div className="space-y-1 rounded-xl border border-neutral-800/80 bg-neutral-950/70 p-4">
                        <span className="text-[11px] font-bold tracking-wider text-neutral-500 uppercase">
                          Who Needs Help
                        </span>
                        <p className="flex items-center gap-2 text-sm font-semibold text-white">
                          <UserCheck className="h-4 w-4 text-indigo-400" />
                          {item.student_name}{' '}
                          <span className="text-xs text-neutral-400">({item.user_id})</span>
                        </p>
                      </div>

                      {/* What happened */}
                      <div className="space-y-1 rounded-xl border border-neutral-800/80 bg-neutral-950/70 p-4">
                        <span className="text-[11px] font-bold tracking-wider text-neutral-500 uppercase">
                          What Happened
                        </span>
                        <p className="text-sm font-medium text-neutral-200 capitalize">
                          {item.reason.replace(/_/g, ' ')}
                        </p>
                      </div>

                      {/* Summary */}
                      <div className="space-y-1 rounded-xl border border-neutral-800/80 bg-neutral-950/70 p-4 md:col-span-2">
                        <span className="text-[11px] font-bold tracking-wider text-neutral-500 uppercase">
                          Agent Summary & Context
                        </span>
                        <p className="border-neutral-850 rounded-lg border bg-neutral-900/60 p-3 font-mono text-xs leading-relaxed text-neutral-300">
                          {item.summary}
                        </p>
                      </div>

                      {/* Language */}
                      <div className="space-y-1 rounded-xl border border-neutral-800/80 bg-neutral-950/70 p-4">
                        <span className="text-[11px] font-bold tracking-wider text-neutral-500 uppercase">
                          Language
                        </span>
                        <p className="text-sm font-semibold text-emerald-400">
                          Hinglish / Devanagari Script
                        </p>
                      </div>

                      {/* Preferred follow up */}
                      <div className="space-y-1 rounded-xl border border-neutral-800/80 bg-neutral-950/70 p-4">
                        <span className="text-[11px] font-bold tracking-wider text-neutral-500 uppercase">
                          Preferred Follow Up
                        </span>
                        <p className="flex items-center gap-2 text-sm font-semibold text-indigo-400">
                          <PhoneCall className="h-4 w-4" />
                          Voice Practice Callback
                        </p>
                      </div>
                    </div>

                    {/* Footer timestamp */}
                    <div className="flex items-center justify-between border-t border-neutral-800/50 pt-2 text-xs text-neutral-500">
                      <div className="flex items-center gap-1.5">
                        <Clock className="h-3.5 w-3.5" />
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
