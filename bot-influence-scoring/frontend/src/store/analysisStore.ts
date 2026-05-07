import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Config {
  tau:   number;
  alpha: number;
  beta1: number;
  beta2: number;
  beta3: number;
}

interface AnalysisStore {
  activeJobId: string | null;
  config: Config;
  setJobId: (id: string | null) => void;
  setConfig: (patch: Partial<Config>) => void;
}

export const useAnalysisStore = create<AnalysisStore>()(
  persist(
    (set) => ({
      activeJobId: null,
      config: { tau: 0.5, alpha: 0.6, beta1: 0.333, beta2: 0.333, beta3: 0.334 },
      setJobId:  (id)    => set({ activeJobId: id }),
      setConfig: (patch) => set((s) => ({ config: { ...s.config, ...patch } })),
    }),
    { name: 'analysis-store' },
  ),
);
