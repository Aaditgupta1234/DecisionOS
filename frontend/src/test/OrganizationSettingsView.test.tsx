import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OrganizationSettingsView } from '../views/settings/OrganizationSettingsView';
import { useOrganization } from '../context/OrganizationContext';
import { DecisionApi } from '../api';

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(),
}));

describe('OrganizationSettingsView Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders organization profile and team members list for OWNER role', async () => {
    const mockOrg = {
      id: 'org-1',
      name: 'Stark Industries',
      slug: 'stark-industries',
      is_active: true,
      created_at: '2026-08-14T00:00:00Z',
      updated_at: '2026-08-14T00:00:00Z',
      current_user_role: 'OWNER' as const,
      member_count: 2,
    };

    (useOrganization as any).mockReturnValue({
      activeOrganization: mockOrg,
      refreshOrganizations: vi.fn(),
      currentRole: 'OWNER',
    });

    vi.spyOn(DecisionApi, 'getOrganization').mockResolvedValue({
      ...mockOrg,
      members: [
        {
          id: 'm1',
          organization_id: 'org-1',
          user_id: 'u1',
          role: 'OWNER',
          email: 'tony@stark.com',
          full_name: 'Tony Stark',
          created_at: '2026-08-14T00:00:00Z',
        },
        {
          id: 'm2',
          organization_id: 'org-1',
          user_id: 'u2',
          role: 'ANALYST',
          email: 'pepper@stark.com',
          full_name: 'Pepper Potts',
          created_at: '2026-08-14T00:00:00Z',
        },
      ],
    });

    render(<OrganizationSettingsView />);

    expect(screen.getByText('Organization Settings')).toBeInTheDocument();

    // Wait for async member table load
    expect(await screen.findByText('Add Team Member')).toBeInTheDocument();
    expect(await screen.findByText('Tony Stark')).toBeInTheDocument();
    expect(screen.getByText('tony@stark.com')).toBeInTheDocument();
    expect(screen.getByText('Pepper Potts')).toBeInTheDocument();
    expect(screen.getByText('pepper@stark.com')).toBeInTheDocument();
  });
});
