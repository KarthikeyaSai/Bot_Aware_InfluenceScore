import { useState, useEffect, useRef } from 'react';

export interface JobProgress {
  step: string;
  pct_complete: number;
  message: string;
}

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress]   = useState<JobProgress | null>(null);
  const [completed, setCompleted] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;
    setCompleted(false);
    setProgress(null);

    wsRef.current = new WebSocket(`ws://localhost:8000/api/v1/ws/jobs/${jobId}`);

    wsRef.current.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.event === 'progress') setProgress(msg);
      else if (msg.event === 'completed') { setCompleted(true); wsRef.current?.close(); }
    };

    return () => wsRef.current?.close();
  }, [jobId]);

  return { progress, completed };
}
