'use client';

import { useState } from 'react';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

interface TaraWelcomeProps {
  onStartCall: () => Promise<void> | void;
}

export function TaraWelcome({ onStartCall }: TaraWelcomeProps) {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleStart = async () => {
    setIsConnecting(true);
    try {
      await onStartCall();
    } catch (err: unknown) {
      console.error(err);
      toast.error('Microphone Access Denied', {
        description:
          'Please click the lock icon in your browser address bar and allow microphone access so Tara can hear you read!',
        duration: 12000,
      });
      setIsConnecting(false);
    }
  };

  return (
    <div className="tara-welcome">
      {/* Animated background blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />

      {/* Floating decorative elements */}
      <div className="floating-letter" style={{ top: '12%', left: '8%', animationDelay: '0s' }}>A</div>
      <div className="floating-letter" style={{ top: '20%', right: '10%', animationDelay: '0.8s' }}>B</div>
      <div className="floating-letter" style={{ top: '60%', left: '5%', animationDelay: '1.6s' }}>क</div>
      <div className="floating-letter" style={{ top: '70%', right: '7%', animationDelay: '0.4s' }}>ख</div>
      <div className="floating-letter" style={{ top: '40%', left: '3%', animationDelay: '2s' }}>C</div>
      <div className="floating-letter" style={{ bottom: '20%', right: '4%', animationDelay: '1.2s' }}>ग</div>
      <div className="floating-star" style={{ top: '15%', left: '25%', animationDelay: '0.3s' }}>✦</div>
      <div className="floating-star" style={{ top: '25%', right: '25%', animationDelay: '1s' }}>✦</div>
      <div className="floating-star" style={{ bottom: '30%', left: '20%', animationDelay: '1.8s' }}>✦</div>

      <div className="tara-card">
        {/* Badge */}
        <div className="tara-badge">
          <span>📚</span>
          <span>VoiceForBharat · Learning & Literacy</span>
        </div>

        {/* Avatar */}
        <div className="tara-avatar-ring">
          <div className="tara-avatar">
            <span className="tara-avatar-emoji">👩‍🏫</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="tara-title">Tara</h1>
        <p className="tara-subtitle">Aapki English Reading Buddy</p>
        <p className="tara-desc">
          Practice reading English words in a fun, safe, and encouraging way.<br />
          Tara speaks Hinglish — just like you!
        </p>

        {/* Feature pills */}
        <div className="tara-pills">
          <span className="pill">🗣️ Hinglish Support</span>
          <span className="pill">📖 Phonics Practice</span>
          <span className="pill">🤗 Never Judges</span>
        </div>

        {/* CTA Button */}
        <button
          onClick={handleStart}
          disabled={isConnecting}
          className="tara-btn"
          id="start-reading-btn"
        >
          {isConnecting ? (
            <>
              <Loader2 className="animate-spin" style={{ width: 20, height: 20, display: 'inline', marginRight: 8 }} />
              Connecting to Tara...
            </>
          ) : (
            <>
              <span style={{ marginRight: 8 }}>🎙️</span>
              Start Reading with Tara
            </>
          )}
        </button>

        {/* Mic tip */}
        <p className="tara-mic-tip">
          🎤 Microphone access required · <span style={{ color: '#FF9933' }}>Hindi + English</span> supported
        </p>
      </div>

      {/* Bottom branding */}
      <div className="tara-bottom-brand">
        Powered by <strong>Murf Falcon</strong> TTS · Built for <strong>#VoiceForBharat</strong>
      </div>
    </div>
  );
}
