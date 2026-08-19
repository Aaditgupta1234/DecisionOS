import React from 'react';
import { usePermissions } from '../../hooks/usePermissions';
import { UserRole } from '../../config/permissionsConfig';

interface RoleGuardProps {
  roles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ roles, children, fallback = null }) => {
  const { hasRole } = usePermissions();

  if (!hasRole(roles)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
