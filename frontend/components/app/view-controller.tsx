'use client';

import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { TaraSessionView } from '@/components/app/tara-session';
import { TaraWelcome } from '@/components/app/tara-welcome';

const VIEW_MOTION_PROPS = {
  variants: {
    visible: { opacity: 1, scale: 1 },
    hidden: { opacity: 0, scale: 0.97 },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: { duration: 0.4, ease: 'easeOut' },
};

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
  const { isConnected, start } = useSessionContext();

  return (
    <AnimatePresence mode="wait">
      {!isConnected && (
        <motion.div
          key="welcome"
          {...VIEW_MOTION_PROPS}
          style={{ width: '100%', minHeight: '100svh' }}
        >
          <TaraWelcome onStartCall={start} />
        </motion.div>
      )}
      {isConnected && (
        <motion.div
          key="session"
          {...VIEW_MOTION_PROPS}
          style={{ width: '100%', minHeight: '100svh' }}
        >
          <TaraSessionView />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
