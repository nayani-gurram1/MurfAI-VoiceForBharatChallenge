'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface CallLog {
  call_id: string;
  user_id: string;
  student_name: string;
  channel: string;
  direction: string;
  status: string;
  failure_reason: string;
  exercises_completed: number;
  duration_seconds: number;
  created_at: string;
}

interface ToolTelemetry {
  tool_name: string;
  executions: number;
  avg_latency_ms: number;
  status: string;
}

interface AnalyticsData {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate_percent: number;
  avg_duration_seconds: number;
  sip_calls: number;
  web_calls: number;
  open_escalations: number;
  failure_breakdown: Record<string, number>;
  categories_breakdown: Record<string, number>;
  duration_distribution: Record<string, number>;
  tools_telemetry: ToolTelemetry[];
  recent_calls: CallLog[];
  last_updated: string;
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    'overview' | 'history' | 'escalations' | 'tools' | 'students'
  >('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics', { cache: 'no-store' });
      const json = await res.json();
      if (json.success) {
        setAnalytics(json.analytics);
        setError(null);
      } else {
        setError(json.error || 'Failed to fetch analytics');
      }
    } catch (err: any) {
      setError('Error connecting to analytics API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    if (!autoRefresh) return;
    const interval = setInterval(fetchAnalytics, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const totalCalls = analytics?.total_calls || 0;
  const succCalls = analytics?.successful_calls || 0;
  const failCalls = analytics?.failed_calls || 0;
  const succRate = analytics?.success_rate_percent || 0.0;
  const avgDur = analytics?.avg_duration_seconds || 0;
  const openEsc = analytics?.open_escalations || 0;
  const recentLogs = analytics?.recent_calls || [];

  return (
    <div
      style={{
        display: 'flex',
        minHeight: '100vh',
        backgroundColor: '#070c16',
        color: '#f8fafc',
        fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
        fontSize: '13px',
      }}
    >
      {/* ── LEFT SIDEBAR ────────────────────────────────────────── */}
      <aside
        style={{
          width: '260px',
          backgroundColor: '#0c1322',
          borderRight: '1px solid rgba(255, 255, 255, 0.07)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '20px 16px',
          flexShrink: 0,
        }}
      >
        <div>
          {/* Logo Brand */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '28px',
              padding: '0 8px',
            }}
          >
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: '#00d26a',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                boxShadow: '0 0 16px rgba(0, 210, 106, 0.4)',
              }}
            >
              🌱
            </div>
            <div>
              <h2
                style={{
                  fontSize: '16px',
                  fontWeight: '800',
                  margin: 0,
                  letterSpacing: '0.5px',
                  color: '#fff',
                }}
              >
                TARA AI
              </h2>
              <span
                style={{
                  fontSize: '10px',
                  color: '#00d26a',
                  fontWeight: '700',
                  letterSpacing: '0.5px',
                }}
              >
                AI VOICE ASSISTANT FOR LEARNERS
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <button
              onClick={() => setActiveTab('overview')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'overview' ? '#00d26a' : 'transparent',
                color: activeTab === 'overview' ? '#000' : '#94a3b8',
                fontWeight: activeTab === 'overview' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                📊 Overview
              </span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'history' ? '#00d26a' : 'transparent',
                color: activeTab === 'history' ? '#000' : '#94a3b8',
                fontWeight: activeTab === 'history' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                📞 Call History
              </span>
              <span
                style={{
                  backgroundColor: activeTab === 'history' ? '#000' : 'rgba(255, 255, 255, 0.1)',
                  color: activeTab === 'history' ? '#fff' : '#00d26a',
                  fontSize: '11px',
                  fontWeight: '700',
                  padding: '2px 7px',
                  borderRadius: '10px',
                }}
              >
                {totalCalls}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('escalations')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'escalations' ? '#00d26a' : 'transparent',
                color: activeTab === 'escalations' ? '#000' : '#94a3b8',
                fontWeight: activeTab === 'escalations' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                🚨 Alerts & Escalations
              </span>
              <span
                style={{
                  backgroundColor: activeTab === 'escalations' ? '#000' : 'rgba(239, 68, 68, 0.2)',
                  color: activeTab === 'escalations' ? '#fff' : '#ef4444',
                  fontSize: '11px',
                  fontWeight: '700',
                  padding: '2px 7px',
                  borderRadius: '10px',
                }}
              >
                {openEsc}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('tools')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'tools' ? '#00d26a' : 'transparent',
                color: activeTab === 'tools' ? '#000' : '#94a3b8',
                fontWeight: activeTab === 'tools' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                🛠️ Tools Usage
              </span>
            </button>

            <button
              onClick={() => setActiveTab('students')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: activeTab === 'students' ? '#00d26a' : 'transparent',
                color: activeTab === 'students' ? '#000' : '#94a3b8',
                fontWeight: activeTab === 'students' ? '700' : '500',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease',
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                👩‍🎓 Students Memory
              </span>
            </button>
          </nav>
        </div>

        {/* Sidebar Footer Agent Status Card */}
        <div
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '12px',
            padding: '14px',
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#00d26a',
                boxShadow: '0 0 8px #00d26a',
              }}
            />
            <span style={{ fontWeight: '700', color: '#fff', fontSize: '12px' }}>
              Tara AI Agent
            </span>
          </div>
          <span style={{ color: '#64748b', fontSize: '11px' }}>● Online • LiveKit SIP</span>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: '4px',
              fontSize: '10px',
              color: '#475569',
            }}
          >
            <span>Version: 1.0.0</span>
            <span>Asia/Kolkata</span>
          </div>
        </div>
      </aside>

      {/* ── MAIN CONTENT AREA ────────────────────────────────────── */}
      <main style={{ flex: 1, padding: '24px 32px', overflowY: 'auto' }}>
        {/* Top Header */}
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '24px',
          }}
        >
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: '800', margin: 0, color: '#fff' }}>
              Good morning, Nayani! 👋
            </h1>
            <p style={{ color: '#64748b', fontSize: '13px', margin: '2px 0 0 0' }}>
              Here's what's happening with your voice agent today.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                padding: '6px 14px',
                borderRadius: '8px',
                color: '#94a3b8',
                fontSize: '12px',
                fontWeight: '500',
              }}
            >
              📅 Today (13/8/2026)
            </span>

            <span
              style={{
                backgroundColor: 'rgba(0, 210, 106, 0.12)',
                border: '1px solid rgba(0, 210, 106, 0.3)',
                color: '#00d26a',
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <span
                style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: '#00d26a',
                }}
              />
              Live SQLite DB
            </span>

            <Link
              href="/"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#fff',
                textDecoration: 'none',
                padding: '7px 16px',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: '600',
              }}
            >
              ← Back to Home
            </Link>

            <Link
              href="/"
              style={{
                backgroundColor: '#00d26a',
                color: '#000',
                textDecoration: 'none',
                padding: '7px 16px',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: '700',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 0 16px rgba(0, 210, 106, 0.3)',
              }}
            >
              🎙️ Start Voice Call
            </Link>
          </div>
        </header>

        {loading ? (
          <div style={{ padding: '60px', textAlign: 'center', color: '#64748b' }}>
            Loading Analytics Engine...
          </div>
        ) : error ? (
          <div
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#f87171',
              padding: '16px',
              borderRadius: '8px',
            }}
          >
            {error}
          </div>
        ) : (
          analytics && (
            <>
              {/* ── TAB 1: OVERVIEW ────────────────────────────────────── */}
              {activeTab === 'overview' && (
                <div>
                  {/* 4 Core Top Cards */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(4, 1fr)',
                      gap: '16px',
                      marginBottom: '24px',
                    }}
                  >
                    {/* TOTAL CALLS */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        position: 'relative',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#64748b',
                            letterSpacing: '0.5px',
                          }}
                        >
                          TOTAL CALLS
                        </span>
                        <span style={{ fontSize: '16px' }}>📞</span>
                      </div>
                      <div
                        style={{
                          fontSize: '38px',
                          fontWeight: '800',
                          color: '#fff',
                          marginTop: '8px',
                        }}
                      >
                        {totalCalls}
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginTop: '12px',
                        }}
                      >
                        <span style={{ fontSize: '11px', color: '#00d26a', fontWeight: '600' }}>
                          Live SQLite DB
                        </span>
                        {/* Sparkline curve */}
                        <svg width="80" height="20" viewBox="0 0 80 20">
                          <path
                            d="M0,15 Q20,5 40,12 T80,3"
                            fill="none"
                            stroke="#00d26a"
                            strokeWidth="2"
                          />
                        </svg>
                      </div>
                    </div>

                    {/* SUCCESSFUL CALLS */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(0, 210, 106, 0.25)',
                        borderRadius: '14px',
                        padding: '20px',
                        boxShadow: '0 4px 20px rgba(0, 210, 106, 0.05)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#00d26a',
                            letterSpacing: '0.5px',
                          }}
                        >
                          SUCCESSFUL CALLS
                        </span>
                        <span
                          style={{
                            backgroundColor: 'rgba(0, 210, 106, 0.15)',
                            color: '#00d26a',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '12px',
                          }}
                        >
                          ✓
                        </span>
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'baseline',
                          gap: '10px',
                          marginTop: '8px',
                        }}
                      >
                        <span style={{ fontSize: '38px', fontWeight: '800', color: '#00d26a' }}>
                          {succCalls}
                        </span>
                        <span
                          style={{
                            fontSize: '13px',
                            fontWeight: '700',
                            color: '#00d26a',
                            backgroundColor: 'rgba(0, 210, 106, 0.15)',
                            padding: '2px 8px',
                            borderRadius: '12px',
                          }}
                        >
                          {succRate}%
                        </span>
                      </div>
                      {/* Sparkline */}
                      <div style={{ marginTop: '12px' }}>
                        <svg width="100%" height="16" viewBox="0 0 160 16">
                          <path
                            d="M0,12 Q40,14 80,6 T160,2"
                            fill="none"
                            stroke="#00d26a"
                            strokeWidth="2.5"
                          />
                        </svg>
                      </div>
                    </div>

                    {/* FAILED CALLS */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(239, 68, 68, 0.25)',
                        borderRadius: '14px',
                        padding: '20px',
                        boxShadow: '0 4px 20px rgba(239, 68, 68, 0.05)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#ef4444',
                            letterSpacing: '0.5px',
                          }}
                        >
                          FAILED CALLS
                        </span>
                        <span
                          style={{
                            backgroundColor: 'rgba(239, 68, 68, 0.15)',
                            color: '#ef4444',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '12px',
                          }}
                        >
                          ✕
                        </span>
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'baseline',
                          gap: '10px',
                          marginTop: '8px',
                        }}
                      >
                        <span style={{ fontSize: '38px', fontWeight: '800', color: '#ef4444' }}>
                          {failCalls}
                        </span>
                        <span
                          style={{
                            fontSize: '13px',
                            fontWeight: '700',
                            color: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.15)',
                            padding: '2px 8px',
                            borderRadius: '12px',
                          }}
                        >
                          {(100 - succRate).toFixed(0)}%
                        </span>
                      </div>
                      {/* Sparkline */}
                      <div style={{ marginTop: '12px' }}>
                        <svg width="100%" height="16" viewBox="0 0 160 16">
                          <path
                            d="M0,4 Q40,6 80,12 T160,14"
                            fill="none"
                            stroke="#ef4444"
                            strokeWidth="2.5"
                          />
                        </svg>
                      </div>
                    </div>

                    {/* SUCCESS RATE */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <span
                          style={{
                            fontSize: '11px',
                            fontWeight: '700',
                            color: '#64748b',
                            letterSpacing: '0.5px',
                          }}
                        >
                          SUCCESS RATE
                        </span>
                        <span style={{ fontSize: '14px' }}>🎯</span>
                      </div>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginTop: '8px',
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '34px', fontWeight: '800', color: '#fff' }}>
                            {succRate}%
                          </div>
                          <span style={{ fontSize: '11px', color: '#00d26a', fontWeight: '600' }}>
                            Goal: &gt;90%
                          </span>
                        </div>
                        {/* Circular Progress Ring */}
                        <svg width="50" height="50" viewBox="0 0 50 50">
                          <circle
                            cx="25"
                            cy="25"
                            r="20"
                            fill="none"
                            stroke="rgba(255, 255, 255, 0.1)"
                            strokeWidth="5"
                          />
                          <circle
                            cx="25"
                            cy="25"
                            r="20"
                            fill="none"
                            stroke="#00d26a"
                            strokeWidth="5"
                            strokeDasharray="125"
                            strokeDashoffset={125 - (125 * succRate) / 100}
                            strokeLinecap="round"
                            transform="rotate(-90 25 25)"
                          />
                        </svg>
                      </div>
                    </div>
                  </div>

                  {/* Middle Grid: Categories + Channels + Escalations */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '2fr 1fr 1fr',
                      gap: '16px',
                      marginBottom: '24px',
                    }}
                  >
                    {/* CALL CATEGORIES BREAKDOWN */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                      }}
                    >
                      <div style={{ marginBottom: '16px' }}>
                        <h3
                          style={{
                            fontSize: '13px',
                            fontWeight: '700',
                            margin: 0,
                            color: '#fff',
                            letterSpacing: '0.5px',
                          }}
                        >
                          CALL CATEGORIES BREAKDOWN
                        </h3>
                        <span style={{ fontSize: '11px', color: '#64748b' }}>
                          Real student inquiries from SQLite
                        </span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        {Object.entries(analytics.categories_breakdown).map(([cat, count]) => {
                          const pct = totalCalls > 0 ? Math.round((count / totalCalls) * 100) : 0;
                          return (
                            <div key={cat}>
                              <div
                                style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  marginBottom: '4px',
                                  fontSize: '12px',
                                }}
                              >
                                <span style={{ color: '#e2e8f0', fontWeight: '500' }}>
                                  🌱 {cat}
                                </span>
                                <span style={{ color: '#00d26a', fontWeight: '700' }}>
                                  {count} calls ({pct}%)
                                </span>
                              </div>
                              <div
                                style={{
                                  width: '100%',
                                  height: '8px',
                                  backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                  borderRadius: '4px',
                                  overflow: 'hidden',
                                }}
                              >
                                <div
                                  style={{
                                    width: `${pct}%`,
                                    height: '100%',
                                    backgroundColor: '#00d26a',
                                    borderRadius: '4px',
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* CALLS BY CHANNEL */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <h3
                        style={{
                          fontSize: '13px',
                          fontWeight: '700',
                          margin: 0,
                          color: '#fff',
                          letterSpacing: '0.5px',
                          alignSelf: 'flex-start',
                        }}
                      >
                        CALLS BY CHANNEL
                      </h3>

                      {/* Donut Chart */}
                      <div
                        style={{
                          position: 'relative',
                          width: '120px',
                          height: '120px',
                          margin: '16px 0',
                        }}
                      >
                        <svg width="120" height="120" viewBox="0 0 120 120">
                          <circle
                            cx="60"
                            cy="60"
                            r="45"
                            fill="none"
                            stroke="#00d26a"
                            strokeWidth="14"
                          />
                          {analytics.sip_calls > 0 && (
                            <circle
                              cx="60"
                              cy="60"
                              r="45"
                              fill="none"
                              stroke="#a855f7"
                              strokeWidth="14"
                              strokeDasharray="282"
                              strokeDashoffset={282 - (282 * analytics.sip_calls) / totalCalls}
                              transform="rotate(-90 60 60)"
                            />
                          )}
                        </svg>
                        <div
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '120px',
                            height: '120px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <span style={{ fontSize: '24px', fontWeight: '800', color: '#fff' }}>
                            {totalCalls}
                          </span>
                          <span style={{ fontSize: '9px', color: '#64748b', fontWeight: '700' }}>
                            TOTAL
                          </span>
                        </div>
                      </div>

                      <div
                        style={{
                          width: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                          fontSize: '11px',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <span
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              color: '#94a3b8',
                            }}
                          >
                            <span
                              style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                backgroundColor: '#a855f7',
                              }}
                            />
                            SIP Calls
                          </span>
                          <span style={{ fontWeight: '700', color: '#fff' }}>
                            {analytics.sip_calls} (
                            {totalCalls > 0
                              ? Math.round((analytics.sip_calls / totalCalls) * 100)
                              : 0}
                            %)
                          </span>
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <span
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              color: '#94a3b8',
                            }}
                          >
                            <span
                              style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                backgroundColor: '#00d26a',
                              }}
                            />
                            Web Calls
                          </span>
                          <span style={{ fontWeight: '700', color: '#fff' }}>
                            {analytics.web_calls} (
                            {totalCalls > 0
                              ? Math.round((analytics.web_calls / totalCalls) * 100)
                              : 100}
                            %)
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* HUMAN ESCALATIONS CARD */}
                    <div
                      style={{
                        backgroundColor: 'rgba(239, 68, 68, 0.05)',
                        border: '1px solid rgba(239, 68, 68, 0.2)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            color: '#ef4444',
                            fontWeight: '700',
                            fontSize: '12px',
                            marginBottom: '12px',
                          }}
                        >
                          <span>🚨</span> HUMAN ESCALATIONS
                        </div>
                        <div style={{ fontSize: '42px', fontWeight: '900', color: '#ef4444' }}>
                          {openEsc}
                        </div>
                        <span style={{ fontSize: '12px', color: '#f87171' }}>
                          Active Dispatch Requests
                        </span>
                      </div>

                      <button
                        onClick={() => setActiveTab('escalations')}
                        style={{
                          width: '100%',
                          backgroundColor: 'rgba(239, 68, 68, 0.2)',
                          border: '1px solid rgba(239, 68, 68, 0.4)',
                          color: '#ef4444',
                          padding: '10px',
                          borderRadius: '8px',
                          fontWeight: '700',
                          fontSize: '12px',
                          cursor: 'pointer',
                          marginTop: '16px',
                        }}
                      >
                        View Escalations ({openEsc}) →
                      </button>
                    </div>
                  </div>

                  {/* Bottom Row: Failure Reasons + Duration Distribution + Recent Logs */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                    {/* FAILURE REASONS */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <h3
                        style={{
                          fontSize: '13px',
                          fontWeight: '700',
                          margin: 0,
                          color: '#fff',
                          letterSpacing: '0.5px',
                        }}
                      >
                        FAILURE REASONS
                      </h3>

                      {/* Donut */}
                      <div
                        style={{
                          position: 'relative',
                          width: '110px',
                          height: '110px',
                          margin: '14px auto',
                        }}
                      >
                        <svg width="110" height="110" viewBox="0 0 110 110">
                          <circle
                            cx="55"
                            cy="55"
                            r="40"
                            fill="none"
                            stroke="#ef4444"
                            strokeWidth="12"
                          />
                        </svg>
                        <div
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '110px',
                            height: '110px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <span style={{ fontSize: '22px', fontWeight: '800', color: '#ef4444' }}>
                            {failCalls}
                          </span>
                          <span style={{ fontSize: '9px', color: '#64748b', fontWeight: '700' }}>
                            FAILURES
                          </span>
                        </div>
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                          fontSize: '11px',
                        }}
                      >
                        {Object.entries(analytics.failure_breakdown).map(([reason, count]) => (
                          <div
                            key={reason}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              color: '#94a3b8',
                            }}
                          >
                            <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span
                                style={{
                                  width: '8px',
                                  height: '8px',
                                  borderRadius: '50%',
                                  backgroundColor: '#ef4444',
                                }}
                              />
                              {reason}
                            </span>
                            <span style={{ fontWeight: '700', color: '#fff' }}>
                              {count} ({failCalls > 0 ? Math.round((count / failCalls) * 100) : 0}%)
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* CALL DURATION DISTRIBUTION */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <h3
                        style={{
                          fontSize: '13px',
                          fontWeight: '700',
                          margin: 0,
                          color: '#fff',
                          letterSpacing: '0.5px',
                        }}
                      >
                        CALL DURATION DISTRIBUTION
                      </h3>

                      {/* Bar Chart Histogram */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'flex-end',
                          justifyContent: 'space-between',
                          height: '100px',
                          margin: '14px 0',
                          paddingBottom: '4px',
                          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                        }}
                      >
                        {Object.entries(analytics.duration_distribution).map(([range, count]) => {
                          const maxC = Math.max(
                            ...Object.values(analytics.duration_distribution),
                            1
                          );
                          const hPct = Math.max(10, Math.round((count / maxC) * 100));
                          return (
                            <div
                              key={range}
                              style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                flex: 1,
                                gap: '4px',
                              }}
                            >
                              <span
                                style={{ fontSize: '10px', color: '#00d26a', fontWeight: '700' }}
                              >
                                {count}
                              </span>
                              <div
                                style={{
                                  width: '18px',
                                  height: `${hPct}%`,
                                  backgroundColor: '#00d26a',
                                  borderRadius: '3px 3px 0 0',
                                }}
                              />
                              <span style={{ fontSize: '9px', color: '#64748b' }}>{range}</span>
                            </div>
                          );
                        })}
                      </div>

                      <div
                        style={{
                          textAlign: 'center',
                          color: '#94a3b8',
                          fontSize: '11px',
                          fontWeight: '600',
                        }}
                      >
                        Average Call Duration: <span style={{ color: '#00d26a' }}>{avgDur}s</span>
                      </div>
                    </div>

                    {/* RECENT CALLS LOG */}
                    <div
                      style={{
                        backgroundColor: '#0f172a',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        borderRadius: '14px',
                        padding: '20px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: '12px',
                        }}
                      >
                        <h3
                          style={{
                            fontSize: '13px',
                            fontWeight: '700',
                            margin: 0,
                            color: '#fff',
                            letterSpacing: '0.5px',
                          }}
                        >
                          RECENT CALLS LOG
                        </h3>
                        <button
                          onClick={() => setActiveTab('history')}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#00d26a',
                            fontSize: '11px',
                            cursor: 'pointer',
                            fontWeight: '600',
                          }}
                        >
                          View All ({totalCalls}) →
                        </button>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {recentLogs.slice(0, 4).map((log) => (
                          <div
                            key={log.call_id}
                            style={{
                              backgroundColor: 'rgba(255, 255, 255, 0.02)',
                              border: '1px solid rgba(255, 255, 255, 0.05)',
                              borderRadius: '8px',
                              padding: '8px 10px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                            }}
                          >
                            <div>
                              <div
                                style={{
                                  fontFamily: 'monospace',
                                  fontSize: '11px',
                                  color: '#e2e8f0',
                                  fontWeight: '600',
                                }}
                              >
                                {log.call_id.substring(0, 22)}
                              </div>
                              <span style={{ fontSize: '10px', color: '#64748b' }}>
                                {log.channel.toUpperCase()} • {log.duration_seconds}s
                              </span>
                            </div>
                            <span
                              style={{
                                backgroundColor:
                                  log.status === 'success'
                                    ? 'rgba(0, 210, 106, 0.15)'
                                    : 'rgba(239, 68, 68, 0.15)',
                                color: log.status === 'success' ? '#00d26a' : '#ef4444',
                                padding: '3px 8px',
                                borderRadius: '4px',
                                fontSize: '10px',
                                fontWeight: '700',
                                textTransform: 'uppercase',
                              }}
                            >
                              {log.status === 'success' ? 'SUCCESS' : 'FAILED'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ── TAB 2: CALL HISTORY ────────────────────────────────── */}
              {activeTab === 'history' && (
                <div
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '14px',
                    padding: '24px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '20px',
                    }}
                  >
                    <div>
                      <h2 style={{ fontSize: '18px', fontWeight: '700', margin: 0, color: '#fff' }}>
                        Full Call History Logs
                      </h2>
                      <span style={{ color: '#64748b', fontSize: '12px' }}>
                        Complete call record database from SQLite
                      </span>
                    </div>
                    <span
                      style={{
                        backgroundColor: '#00d26a',
                        color: '#000',
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontWeight: '700',
                        fontSize: '12px',
                      }}
                    >
                      {totalCalls} Total Calls Logged
                    </span>
                  </div>

                  <table
                    style={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      fontSize: '12px',
                      textAlign: 'left',
                    }}
                  >
                    <thead>
                      <tr
                        style={{
                          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                          color: '#64748b',
                        }}
                      >
                        <th style={{ padding: '12px' }}>CHANNEL / CALL ID</th>
                        <th style={{ padding: '12px' }}>STUDENT NAME</th>
                        <th style={{ padding: '12px' }}>EXERCISES</th>
                        <th style={{ padding: '12px' }}>DURATION</th>
                        <th style={{ padding: '12px' }}>STATUS</th>
                        <th style={{ padding: '12px' }}>REASON</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentLogs.map((log) => (
                        <tr
                          key={log.call_id}
                          style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}
                        >
                          <td
                            style={{ padding: '12px', fontFamily: 'monospace', color: '#00d26a' }}
                          >
                            {log.channel.toUpperCase()} / {log.call_id}
                          </td>
                          <td style={{ padding: '12px', fontWeight: '600', color: '#fff' }}>
                            {log.student_name}
                          </td>
                          <td
                            style={{
                              padding: '12px',
                              color: log.exercises_completed > 0 ? '#00d26a' : '#64748b',
                            }}
                          >
                            {log.exercises_completed} exercises
                          </td>
                          <td style={{ padding: '12px', color: '#cbd5e1' }}>
                            {log.duration_seconds}s
                          </td>
                          <td style={{ padding: '12px' }}>
                            <span
                              style={{
                                backgroundColor:
                                  log.status === 'success'
                                    ? 'rgba(0, 210, 106, 0.15)'
                                    : 'rgba(239, 68, 68, 0.15)',
                                color: log.status === 'success' ? '#00d26a' : '#ef4444',
                                padding: '3px 8px',
                                borderRadius: '4px',
                                fontSize: '11px',
                                fontWeight: '700',
                              }}
                            >
                              {log.status.toUpperCase()}
                            </span>
                          </td>
                          <td style={{ padding: '12px', color: '#94a3b8' }}>
                            {log.failure_reason || 'None'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* ── TAB 3: TOOLS USAGE TELEMETRY ───────────────────────── */}
              {activeTab === 'tools' && (
                <div>
                  <div style={{ marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: '700', margin: 0, color: '#fff' }}>
                      Agent Tools & Function Telemetry
                    </h2>
                    <span style={{ color: '#64748b', fontSize: '12px' }}>
                      Real-time function execution stats across active voice calls
                    </span>
                  </div>

                  <div
                    style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}
                  >
                    {analytics.tools_telemetry.map((tool) => (
                      <div
                        key={tool.tool_name}
                        style={{
                          backgroundColor: '#0f172a',
                          border: '1px solid rgba(255, 255, 255, 0.08)',
                          borderRadius: '14px',
                          padding: '20px',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            marginBottom: '12px',
                          }}
                        >
                          <span
                            style={{
                              fontSize: '11px',
                              color: '#00d26a',
                              fontWeight: '700',
                              backgroundColor: 'rgba(0, 210, 106, 0.15)',
                              padding: '2px 8px',
                              borderRadius: '4px',
                            }}
                          >
                            {tool.status}
                          </span>
                        </div>
                        <h4
                          style={{
                            fontSize: '14px',
                            fontWeight: '700',
                            color: '#fff',
                            margin: '0 0 6px 0',
                            fontFamily: 'monospace',
                          }}
                        >
                          {tool.tool_name}
                        </h4>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                          Executions:{' '}
                          <strong style={{ color: '#00d26a' }}>{tool.executions} calls</strong>
                        </span>
                        <div style={{ marginTop: '12px', fontSize: '11px', color: '#64748b' }}>
                          Avg Latency:{' '}
                          <strong style={{ color: '#fff' }}>{tool.avg_latency_ms}ms</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── TAB 4: HUMAN ESCALATIONS ───────────────────────────── */}
              {activeTab === 'escalations' && (
                <div
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    borderRadius: '14px',
                    padding: '24px',
                  }}
                >
                  <h2
                    style={{
                      fontSize: '18px',
                      fontWeight: '700',
                      margin: '0 0 16px 0',
                      color: '#ef4444',
                    }}
                  >
                    🚨 Active Human Teacher Escalations ({openEsc})
                  </h2>
                  <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '20px' }}>
                    Student help requests created during Day 7 voice calls. Consent granted for
                    teacher review within 24-48 hours.
                  </p>

                  {openEsc === 0 ? (
                    <div
                      style={{
                        color: '#00d26a',
                        padding: '24px',
                        textAlign: 'center',
                        fontWeight: '600',
                      }}
                    >
                      ✓ No active escalations pending! All learners satisfied.
                    </div>
                  ) : (
                    <Link
                      href="/escalations"
                      style={{
                        backgroundColor: '#ef4444',
                        color: '#fff',
                        textDecoration: 'none',
                        padding: '10px 20px',
                        borderRadius: '8px',
                        fontWeight: '700',
                        display: 'inline-block',
                      }}
                    >
                      Open Full Escalations Portal →
                    </Link>
                  )}
                </div>
              )}

              {/* ── TAB 5: STUDENTS MEMORY ──────────────────────────────── */}
              {activeTab === 'students' && (
                <div
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '14px',
                    padding: '24px',
                  }}
                >
                  <h2
                    style={{
                      fontSize: '18px',
                      fontWeight: '700',
                      margin: '0 0 8px 0',
                      color: '#fff',
                    }}
                  >
                    👩‍🎓 Student Memory Database (Day 4)
                  </h2>
                  <p style={{ color: '#94a3b8', fontSize: '13px' }}>
                    Active profiles stored in SQLite memory including last topics practiced, level,
                    and opt-out preferences.
                  </p>
                </div>
              )}
            </>
          )
        )}
      </main>
    </div>
  );
}
