import { create } from 'zustand';
import { UserRole } from '../config/permissionsConfig';

export interface Organization {
  id: string;
  name: string;
  plan: 'ENTERPRISE_PRO' | 'SCALE' | 'GROWTH';
  activeWorkspacesCount: number;
}

export interface Workspace {
  id: string;
  orgId: string;
  name: string;
  region: string;
  currency: string;
}

interface TenantState {
  activeOrg: Organization;
  activeWorkspace: Workspace;
  userRole: UserRole;
  organizations: Organization[];
  workspaces: Workspace[];
  setActiveOrg: (org: Organization) => void;
  setActiveWorkspace: (workspace: Workspace) => void;
  setUserRole: (role: UserRole) => void;
}

export const useTenantStore = create<TenantState>((set) => ({
  activeOrg: {
    id: 'org-enterprise-001',
    name: 'Apex Global Technologies Group',
    plan: 'ENTERPRISE_PRO',
    activeWorkspacesCount: 4,
  },
  activeWorkspace: {
    id: 'ws-na-prod-001',
    orgId: 'org-enterprise-001',
    name: 'North America Enterprise Operations',
    region: 'us-east-1',
    currency: 'USD',
  },
  userRole: 'ADMIN',
  organizations: [
    {
      id: 'org-enterprise-001',
      name: 'Apex Global Technologies Group',
      plan: 'ENTERPRISE_PRO',
      activeWorkspacesCount: 4,
    },
    {
      id: 'org-logistics-002',
      name: 'Global Freight & Fulfillment Corp',
      plan: 'ENTERPRISE_PRO',
      activeWorkspacesCount: 2,
    },
  ],
  workspaces: [
    {
      id: 'ws-na-prod-001',
      orgId: 'org-enterprise-001',
      name: 'North America Enterprise Operations',
      region: 'us-east-1',
      currency: 'USD',
    },
    {
      id: 'ws-eu-prod-002',
      orgId: 'org-enterprise-001',
      name: 'Europe & UK Retail Logistics',
      region: 'eu-central-1',
      currency: 'EUR',
    },
    {
      id: 'ws-apac-prod-003',
      orgId: 'org-enterprise-001',
      name: 'APAC Expansion Hub',
      region: 'ap-southeast-1',
      currency: 'SGD',
    },
  ],
  setActiveOrg: (org) => set({ activeOrg: org }),
  setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
  setUserRole: (role) => set({ userRole: role }),
}));
