import React, { useEffect, useState } from 'react';
import { useOrganization } from '../../context/OrganizationContext';
import { DecisionApi } from '../../api';
import { OrganizationDetail, OrganizationMember, OrgRole } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import {
  Building2,
  Users,
  Shield,
  UserPlus,
  Trash2,
  Edit2,
  Check,
  AlertCircle,
} from 'lucide-react';

export const OrganizationSettingsView: React.FC = () => {
  const { activeOrganization, refreshOrganizations, currentRole } = useOrganization();
  const [details, setDetails] = useState<OrganizationDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Edit Org Form State
  const [orgName, setOrgName] = useState<string>('');
  const [isSavingOrg, setIsSavingOrg] = useState<boolean>(false);

  // Invite Member Form State
  const [inviteEmail, setInviteEmail] = useState<string>('');
  const [inviteRole, setInviteRole] = useState<OrgRole>('ANALYST');
  const [isInviting, setIsInviting] = useState<boolean>(false);

  const isOwnerOrAdmin = currentRole === 'OWNER' || currentRole === 'ADMIN';

  const loadDetails = async () => {
    if (!activeOrganization) return;
    try {
      setLoading(true);
      setError(null);
      const res = await DecisionApi.getOrganization(activeOrganization.id);
      setDetails(res);
      setOrgName(res.name);
    } catch (err: any) {
      console.error('Failed to load organization details:', err);
      setError(err?.message || 'Could not load organization details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetails();
  }, [activeOrganization?.id]);

  const handleUpdateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeOrganization || !orgName.trim()) return;

    try {
      setIsSavingOrg(true);
      setError(null);
      await DecisionApi.updateOrganization(activeOrganization.id, { name: orgName.trim() });
      setSuccessMsg('Organization settings updated successfully.');
      await refreshOrganizations();
      await loadDetails();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update organization.');
    } finally {
      setIsSavingOrg(false);
    }
  };

  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeOrganization || !inviteEmail.trim()) return;

    try {
      setIsInviting(true);
      setError(null);
      await DecisionApi.addOrganizationMember(activeOrganization.id, {
        email: inviteEmail.trim(),
        role: inviteRole,
      });
      setInviteEmail('');
      setSuccessMsg(`Member '${inviteEmail.trim()}' added successfully.`);
      await loadDetails();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to add member.');
    } finally {
      setIsInviting(false);
    }
  };

  const handleRoleChange = async (memberId: string, newRole: OrgRole) => {
    if (!activeOrganization) return;
    try {
      setError(null);
      await DecisionApi.updateMemberRole(activeOrganization.id, memberId, newRole);
      setSuccessMsg('Member role updated.');
      await loadDetails();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update member role.');
    }
  };

  const handleRemoveMember = async (memberId: string, memberEmail?: string) => {
    if (!activeOrganization) return;
    if (!window.confirm(`Are you sure you want to remove member ${memberEmail || ''} from this organization?`)) return;

    try {
      setError(null);
      await DecisionApi.removeOrganizationMember(activeOrganization.id, memberId);
      setSuccessMsg('Member removed successfully.');
      await loadDetails();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || 'Failed to remove member.');
    }
  };

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case 'OWNER':
        return 'badge-danger';
      case 'ADMIN':
        return 'badge-warning';
      case 'ANALYST':
        return 'badge-primary';
      default:
        return 'badge-neutral';
    }
  };

  if (!activeOrganization) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Organization Selected"
          description="Select or create an organization workspace to manage settings and team members."
          icon={Building2}
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span className="badge badge-primary">SaaS Multi-Tenancy</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Organization ID: {activeOrganization.id}
          </span>
        </div>
        <h1>Organization Settings</h1>
        <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
          Manage your organization workspace profile, team members, and role-based permissions.
        </p>
      </div>

      {error && <ErrorBanner message={error} />}
      {successMsg && (
        <div
          className="card"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderColor: 'var(--color-success)',
            color: 'var(--color-success)',
            marginBottom: '16px',
            fontSize: '0.85rem',
          }}
        >
          <Check size={16} />
          <span>{successMsg}</span>
        </div>
      )}

      {loading ? (
        <LoadingSkeleton count={3} height="120px" />
      ) : details ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Organization Profile Card */}
          <div className="card-elevated">
            <h3 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Building2 size={18} color="var(--color-primary-light)" />
              <span>Workspace Profile</span>
            </h3>

            <form onSubmit={handleUpdateOrg} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', maxWidth: '700px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Organization Name
                </label>
                <input
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  disabled={!isOwnerOrAdmin || isSavingOrg}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    backgroundColor: 'var(--bg-app)',
                    border: '1px solid var(--border-default)',
                    borderRadius: 'var(--radius-sm)',
                    color: '#ffffff',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Workspace Slug
                </label>
                <input
                  type="text"
                  value={details.slug}
                  disabled
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    backgroundColor: 'var(--bg-app)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-muted)',
                    fontSize: '0.85rem',
                  }}
                />
              </div>

              {isOwnerOrAdmin && (
                <div style={{ gridColumn: 'span 2', display: 'flex', justifyContent: 'flex-start', marginTop: '4px' }}>
                  <button type="submit" disabled={isSavingOrg || orgName === details.name} className="btn btn-primary btn-sm">
                    <span>{isSavingOrg ? 'Saving...' : 'Save Profile'}</span>
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Add Team Member Card */}
          {isOwnerOrAdmin && (
            <div className="card-elevated">
              <h3 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <UserPlus size={18} color="var(--color-primary-light)" />
                <span>Add Team Member</span>
              </h3>

              <form onSubmit={handleInviteMember} style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                <div style={{ flex: '1', minWidth: '220px' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    User Email
                  </label>
                  <input
                    type="email"
                    placeholder="colleague@company.com"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      backgroundColor: 'var(--bg-app)',
                      border: '1px solid var(--border-default)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#ffffff',
                      fontSize: '0.85rem',
                    }}
                  />
                </div>

                <div style={{ width: '160px' }}>
                  <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Tenant Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as OrgRole)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      backgroundColor: 'var(--bg-app)',
                      border: '1px solid var(--border-default)',
                      borderRadius: 'var(--radius-sm)',
                      color: '#ffffff',
                      fontSize: '0.85rem',
                    }}
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="ANALYST">ANALYST</option>
                    <option value="VIEWER">VIEWER</option>
                    {currentRole === 'OWNER' && <option value="OWNER">OWNER</option>}
                  </select>
                </div>

                <button type="submit" disabled={isInviting || !inviteEmail.trim()} className="btn btn-primary" style={{ gap: '6px' }}>
                  <UserPlus size={16} />
                  <span>{isInviting ? 'Adding...' : 'Add Member'}</span>
                </button>
              </form>
            </div>
          )}

          {/* Team Members List */}
          <div className="card-elevated">
            <h3 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Users size={18} color="var(--color-primary-light)" />
              <span>Team Members ({details.members.length})</span>
            </h3>

            <div style={{ overflowX: 'auto' }}>
              <table className="report-table" style={{ width: '100%' }}>
                <thead>
                  <tr>
                    <th>MEMBER</th>
                    <th>EMAIL</th>
                    <th>ROLE</th>
                    <th>JOINED</th>
                    {isOwnerOrAdmin && <th>ACTIONS</th>}
                  </tr>
                </thead>
                <tbody>
                  {details.members.map((m: OrganizationMember) => (
                    <tr key={m.id}>
                      <td style={{ fontWeight: 600, color: '#ffffff' }}>{m.full_name || 'Team Member'}</td>
                      <td style={{ color: 'var(--text-secondary)' }}>{m.email}</td>
                      <td>
                        {isOwnerOrAdmin ? (
                          <select
                            value={m.role}
                            onChange={(e) => handleRoleChange(m.id, e.target.value as OrgRole)}
                            style={{
                              padding: '4px 8px',
                              backgroundColor: 'var(--bg-app)',
                              border: '1px solid var(--border-subtle)',
                              borderRadius: 'var(--radius-sm)',
                              color: '#ffffff',
                              fontSize: '0.75rem',
                            }}
                          >
                            <option value="OWNER">OWNER</option>
                            <option value="ADMIN">ADMIN</option>
                            <option value="ANALYST">ANALYST</option>
                            <option value="VIEWER">VIEWER</option>
                          </select>
                        ) : (
                          <span className={`badge ${getRoleBadgeClass(m.role)}`}>{m.role}</span>
                        )}
                      </td>
                      <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(m.created_at).toLocaleDateString()}
                      </td>
                      {isOwnerOrAdmin && (
                        <td>
                          <button
                            onClick={() => handleRemoveMember(m.id, m.email)}
                            className="btn btn-ghost btn-sm"
                            title="Remove member"
                            style={{ color: 'var(--color-danger)', padding: '4px 8px' }}
                          >
                            <Trash2 size={14} />
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
