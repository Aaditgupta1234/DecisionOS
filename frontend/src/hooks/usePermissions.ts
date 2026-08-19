import { useTenantStore } from '../store/useTenantStore';
import { ROLE_PERMISSIONS, PermissionKey, UserRole } from '../config/permissionsConfig';

export const usePermissions = () => {
  const { userRole, setUserRole } = useTenantStore();

  const hasPermission = (permission: PermissionKey | string): boolean => {
    if (!permission) return true;
    const allowed = ROLE_PERMISSIONS[userRole] || [];
    return allowed.includes(permission as PermissionKey);
  };

  const hasRole = (roles: UserRole[]): boolean => {
    return roles.includes(userRole);
  };

  return {
    userRole,
    setUserRole,
    hasPermission,
    hasRole,
  };
};
