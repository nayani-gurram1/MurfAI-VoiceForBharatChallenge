'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { AnimatePresence, motion } from 'motion/react';
import { useAgent, useSessionContext, useSessionMessages } from '@livekit/components-react';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
import { AgentControlBar } from '@/components/agents-ui/agent-control-bar';

type AgentState =
  | 'connecting'
  | 'connected'
  | 'listening'
  | 'thinking'
  | 'speaking'
  | 'disconnected'
  | undefined;

function getStateLabel(agentState: AgentState, messageCount: number): string {
  if (agentState === 'connecting') return 'Connecting to Tara...';
  if (agentState === 'thinking') return 'Tara is thinking...';
  if (agentState === 'speaking') return 'Tara is speaking 🔊';
  if (agentState === 'listening') return 'Listening to you... 🎙️';
  if (messageCount === 0) return 'Tara is ready! Start speaking...';
  return '';
}

function getStateColor(agentState: AgentState): string {
  if (agentState === 'speaking') return '#FF9933';
  if (agentState === 'listening') return '#0D9488';
  if (agentState === 'thinking') return '#8B5CF6';
  return '#9CA3AF';
}

function getAvatarPulse(agentState: AgentState): string {
  if (agentState === 'speaking') return 'pulse-orange';
  if (agentState === 'listening') return 'pulse-teal';
  if (agentState === 'thinking') return 'pulse-purple';
  return '';
}

export function TaraSessionView() {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(true);
  const { state: agentState } = useAgent();

  const controls = {
    leave: true,
    microphone: true,
    chat: true,
    camera: false,
    screenShare: false,
  };

  return (
    <div className="tara-session">
      {/* Background */}
      <div className="session-blob session-blob-1" />
      <div className="session-blob session-blob-2" />

      {/* Top bar */}
      <div className="session-topbar">
        <div className="session-brand">
          <span className="session-brand-emoji">📚</span>
          <span className="session-brand-name">Tara</span>
          <span className="session-brand-sub">Reading Buddy</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/escalations"
            target="_blank"
            className="flex items-center gap-1.5 rounded-lg border border-indigo-700/60 bg-indigo-950/80 px-3 py-1.5 text-xs font-semibold text-indigo-300 transition hover:bg-indigo-900"
          >
            <span>👩‍🏫</span> Human Help Desk (Day 7)
          </Link>
          <div className="session-powered">
            Powered by <strong>Murf Falcon</strong>
          </div>
        </div>
      </div>

      {/* Avatar + state */}
      <div className="session-avatar-area">
        <div className={`session-avatar-ring ${getAvatarPulse(agentState as AgentState)}`}>
          <div className="session-avatar">
            <span>👩‍🏫</span>
          </div>
        </div>
        <AnimatePresence mode="wait">
          <motion.div
            key={agentState ?? 'idle'}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
            className="session-state-label"
            style={{ color: getStateColor(agentState as AgentState) }}
          >
            {getStateLabel(agentState as AgentState, messages.length)}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Chat Transcript */}
      <div className="session-transcript-wrapper">
        <AgentChatTranscript
          agentState={agentState as any}
          messages={messages}
          className="session-transcript"
        />
      </div>

      {/* Control bar */}
      <div className="session-controls">
        <AgentControlBar
          variant="livekit"
          controls={controls}
          isChatOpen={chatOpen}
          isConnected={session.isConnected}
          onDisconnect={session.end}
          onIsChatOpenChange={setChatOpen}
        />
      </div>
    </div>
  );
}
