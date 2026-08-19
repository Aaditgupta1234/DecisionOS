import { create } from 'zustand';

export interface SavedView {
  id: string;
  name: string;
  rolePreset: 'CFO' | 'COO' | 'CRO' | 'RISK_OFFICER' | 'CUSTOM';
  description: string;
  filters: Record<string, any>;
  isDefault?: boolean;
}

interface SavedViewsState {
  savedViews: SavedView[];
  activeViewId: string;
  setActiveViewId: (id: string) => void;
  addSavedView: (view: SavedView) => void;
}

export const useSavedViewsStore = create<SavedViewsState>((set) => ({
  savedViews: [
    {
      id: 'view-cfo-default',
      name: 'CFO Executive View',
      rolePreset: 'CFO',
      description: 'Capital allocation ROI, ARR recovery ledger, and dynamic pricing hedges',
      filters: { focus: 'FINANCIAL' },
      isDefault: true,
    },
    {
      id: 'view-coo-ops',
      name: 'COO Operations & Logistics Radar',
      rolePreset: 'COO',
      description: 'Southeastern courier throughput, delivery latency SLAs, and regional fulfillment',
      filters: { focus: 'OPERATIONS' },
    },
    {
      id: 'view-risk-governance',
      name: 'Chief Risk Officer Radar',
      rolePreset: 'RISK_OFFICER',
      description: 'Policy rule enforcement, customer revenue concentration, and 90-day risk radar',
      filters: { focus: 'RISK' },
    },
  ],
  activeViewId: 'view-cfo-default',
  setActiveViewId: (id) => set({ activeViewId: id }),
  addSavedView: (view) => set((state) => ({ savedViews: [...state.savedViews, view] })),
}));
