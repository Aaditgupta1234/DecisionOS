import React, { useState, useRef, useEffect } from 'react';
import { useOrganization } from '../../context/OrganizationContext';
import { Building2, ChevronDown, Check, Plus, Settings, Shield } from 'lucide-react';
import { Link } from 'react-router-dom';

export const OrganizationSwitcher: React.FC = () => {
  const { organizations, activeOrganization, setActiveOrganization, createOrganization } = useOrganization();
  const [isOpen, setIsOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setIsCreating(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    try {
      await createOrganization(newOrgName.trim());
      setNewOrgName('');
      setIsCreating(false);
      setIsOpen(false);
    } catch (err) {
      console.error('Failed to create organization:', err);
    }
  };

  const getRoleBadgeClass = (role?: string) => {
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

  return (
    <div ref={dropdownRef} style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="btn btn-ghost"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--bg-surface)',
        }}
      >
        <Building2 size={16} color="var(--color-primary-light)" />
        <span style={{ fontWeight: 600, fontSize: '0.85rem', maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {activeOrganization?.name || 'Select Workspace'}
        </span>
        {activeOrganization?.current_user_role && (
          <span className={`badge ${getRoleBadgeClass(activeOrganization.current_user_role)}`} style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
            {activeOrganization.current_user_role}
          </span>
        )}
        <ChevronDown size={14} color="var(--text-muted)" />
      </button>

      {isOpen && (
        <div
          className="card"
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            width: '260px',
            padding: '8px',
            boxShadow: 'var(--shadow-xl)',
            zIndex: 100,
            backgroundColor: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-default)',
          }}
        >
          <div style={{ padding: '6px 10px', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Organizations & Workspaces
          </div>

          <div style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '8px' }}>
            {organizations.map((org) => {
              const isSelected = org.id === activeOrganization?.id;
              return (
                <button
                  key={org.id}
                  onClick={() => {
                    setActiveOrganization(org);
                    setIsOpen(false);
                  }}
                  className="btn btn-ghost"
                  style={{
                    width: '100%',
                    justifyContent: 'space-between',
                    padding: '8px 10px',
                    fontSize: '0.85rem',
                    backgroundColor: isSelected ? 'var(--bg-app)' : 'transparent',
                    borderRadius: 'var(--radius-sm)',
                    marginBottom: '2px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                    <span style={{ fontWeight: isSelected ? 600 : 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {org.name}
                    </span>
                    {org.current_user_role && (
                      <span className={`badge ${getRoleBadgeClass(org.current_user_role)}`} style={{ fontSize: '0.6rem' }}>
                        {org.current_user_role}
                      </span>
                    )}
                  </div>
                  {isSelected && <Check size={14} color="var(--color-primary-light)" />}
                </button>
              );
            })}
          </div>

          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '6px' }}>
            {isCreating ? (
              <form onSubmit={handleCreate} style={{ padding: '4px' }}>
                <input
                  type="text"
                  placeholder="Organization name..."
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  autoFocus
                  style={{
                    width: '100%',
                    padding: '6px 8px',
                    fontSize: '0.8rem',
                    backgroundColor: 'var(--bg-app)',
                    border: '1px solid var(--border-default)',
                    borderRadius: 'var(--radius-sm)',
                    color: '#ffffff',
                    marginBottom: '6px',
                  }}
                />
                <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                  <button
                    type="button"
                    onClick={() => setIsCreating(false)}
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary btn-sm"
                    style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                    disabled={!newOrgName.trim()}
                  >
                    Create
                  </button>
                </div>
              </form>
            ) : (
              <>
                <button
                  onClick={() => setIsCreating(true)}
                  className="btn btn-ghost btn-sm"
                  style={{ width: '100%', justifyContent: 'flex-start', gap: '6px', fontSize: '0.8rem', padding: '6px 8px' }}
                >
                  <Plus size={14} />
                  <span>Create Organization</span>
                </button>

                <Link
                  to="/settings/organization"
                  onClick={() => setIsOpen(false)}
                  className="btn btn-ghost btn-sm"
                  style={{ width: '100%', justifyContent: 'flex-start', gap: '6px', fontSize: '0.8rem', padding: '6px 8px', textDecoration: 'none' }}
                >
                  <Settings size={14} />
                  <span>Organization Settings</span>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
