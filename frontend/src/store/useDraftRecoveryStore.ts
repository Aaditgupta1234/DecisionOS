import { create } from 'zustand';

export interface DraftSnapshot {
  id: string;
  formType: 'SCENARIO_BUILDER' | 'REPORT_EDITOR' | 'PLAYBOOK_STUDIO' | 'GOVERNANCE_DECISION';
  timestamp: string;
  title: string;
  data: Record<string, any>;
}

interface DraftRecoveryState {
  drafts: Record<string, DraftSnapshot>;
  saveDraft: (key: string, draft: DraftSnapshot) => void;
  getDraft: (key: string) => DraftSnapshot | undefined;
  clearDraft: (key: string) => void;
}

export const useDraftRecoveryStore = create<DraftRecoveryState>((set, get) => ({
  drafts: {},
  saveDraft: (key, draft) => {
    set((state) => ({
      drafts: { ...state.drafts, [key]: draft },
    }));
  },
  getDraft: (key) => get().drafts[key],
  clearDraft: (key) => {
    set((state) => {
      const next = { ...state.drafts };
      delete next[key];
      return { drafts: next };
    });
  },
}));
