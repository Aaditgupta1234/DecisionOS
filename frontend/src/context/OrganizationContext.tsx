import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Organization, OrgRole } from '../types';
import { DecisionApi } from '../api';

interface OrganizationContextType {
  organizations: Organization[];
  activeOrganization: Organization | null;
  currentRole: OrgRole | null;
  loading: boolean;
  error: string | null;
  setActiveOrganization: (org: Organization) => void;
  refreshOrganizations: () => Promise<void>;
  createOrganization: (name: string, slug?: string) => Promise<Organization>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export const OrganizationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [activeOrganization, setActiveOrganizationState] = useState<Organization | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listOrganizations();
      const list = Array.isArray(data) ? data : [];
      setOrganizations(list);

      let savedId: string | null = null;
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          savedId = window.localStorage.getItem('decisionos_active_org_id');
        }
      } catch {
        // Safe fallback
      }

      const matched = list.find((o) => o.id === savedId);
      if (matched) {
        setActiveOrganizationState(matched);
      } else if (list.length > 0) {
        setActiveOrganizationState(list[0]);
        try {
          if (typeof window !== 'undefined' && window.localStorage) {
            window.localStorage.setItem('decisionos_active_org_id', list[0].id);
          }
        } catch {}
      } else {
        setActiveOrganizationState(null);
      }
    } catch (err: any) {
      console.warn('Failed to load organizations, fallback to local workspace:', err);
      // Fallback local organization for offline / development
      const fallbackOrg: Organization = {
        id: 'org-default-1',
        name: 'Enterprise Workspace',
        slug: 'enterprise-workspace',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        current_user_role: 'OWNER',
        member_count: 1,
      };
      setOrganizations([fallbackOrg]);
      setActiveOrganizationState(fallbackOrg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshOrganizations();
  }, []);

  const setActiveOrganization = (org: Organization) => {
    setActiveOrganizationState(org);
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem('decisionos_active_org_id', org.id);
      }
    } catch {}
  };

  const createOrganization = async (name: string, slug?: string): Promise<Organization> => {
    const newOrg = await DecisionApi.createOrganization({ name, slug });
    await refreshOrganizations();
    setActiveOrganization(newOrg);
    return newOrg;
  };

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        activeOrganization,
        currentRole: activeOrganization?.current_user_role || 'OWNER',
        loading,
        error,
        setActiveOrganization,
        refreshOrganizations,
        createOrganization,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
};

const defaultOrganizationContext: OrganizationContextType = {
  organizations: [],
  activeOrganization: null,
  currentRole: null,
  loading: false,
  error: null,
  setActiveOrganization: () => {},
  refreshOrganizations: async () => {},
  createOrganization: async () => ({
    id: 'org-default',
    name: 'Default',
    slug: 'default',
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }),
};

export const useOrganization = (): OrganizationContextType => {
  const context = useContext(OrganizationContext);
  return context || defaultOrganizationContext;
};
