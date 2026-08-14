import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OrganizationSwitcher } from '../components/layout/OrganizationSwitcher';
import { useOrganization } from '../context/OrganizationContext';

vi.mock('../context/OrganizationContext', () => ({
  useOrganization: vi.fn(),
}));

describe('OrganizationSwitcher Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders active organization name, user role badge, and opens dropdown on click', () => {
    const mockOrg = {
      id: 'org-1',
      name: 'Acme Global Corp',
      slug: 'acme-global',
      is_active: true,
      created_at: '2026-08-14T00:00:00Z',
      updated_at: '2026-08-14T00:00:00Z',
      current_user_role: 'OWNER' as const,
      member_count: 5,
    };

    (useOrganization as any).mockReturnValue({
      organizations: [mockOrg],
      activeOrganization: mockOrg,
      setActiveOrganization: vi.fn(),
      createOrganization: vi.fn(),
    });

    render(
      <BrowserRouter>
        <OrganizationSwitcher />
      </BrowserRouter>
    );

    // Shows active organization name and OWNER badge
    expect(screen.getByText('Acme Global Corp')).toBeInTheDocument();
    expect(screen.getByText('OWNER')).toBeInTheDocument();

    // Clicking button opens dropdown
    fireEvent.click(screen.getByRole('button', { name: /Acme Global Corp/ }));
    expect(screen.getByText('Organizations & Workspaces')).toBeInTheDocument();
    expect(screen.getByText('Organization Settings')).toBeInTheDocument();
  });
});
