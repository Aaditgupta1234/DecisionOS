import { create } from 'zustand';

interface FeatureFlagsState {
  ENABLE_COPILOT: boolean;
  ENABLE_DIGITAL_TWIN: boolean;
  ENABLE_BENCHMARKING: boolean;
  ENABLE_ENTERPRISE_OS: boolean;
  ENABLE_AUTONOMOUS_AGENTS: boolean;
  ENABLE_CAPITAL_ALLOCATION: boolean;
  ENABLE_AUTONOMOUS_PLAYBOOKS: boolean;
  ENABLE_QUERY_DEVTOOLS: boolean;
  toggleFlag: (flag: keyof Omit<FeatureFlagsState, 'toggleFlag'>) => void;
}

export const useFeatureFlagsStore = create<FeatureFlagsState>((set) => ({
  ENABLE_COPILOT: true,
  ENABLE_DIGITAL_TWIN: true,
  ENABLE_BENCHMARKING: true,
  ENABLE_ENTERPRISE_OS: true,
  ENABLE_AUTONOMOUS_AGENTS: true,
  ENABLE_CAPITAL_ALLOCATION: true,
  ENABLE_AUTONOMOUS_PLAYBOOKS: true,
  ENABLE_QUERY_DEVTOOLS: false,
  toggleFlag: (flag) => set((state) => ({ [flag]: !state[flag] })),
}));
