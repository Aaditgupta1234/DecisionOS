import React from 'react';
import { usePermissions } from '../../hooks/usePermissions';
import { PermissionKey } from '../../config/permissionsConfig';

interface PermissionGuardProps {
  permission: PermissionKey | string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  children,
  fallback = null,
}) => {
  const { hasPermission } = usePermissions();

  if (!hasPermission(permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
