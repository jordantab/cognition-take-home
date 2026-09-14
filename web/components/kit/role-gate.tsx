import type { User } from "@/lib/types";

export function can(user: User, permission: string): boolean {
  return user.permissions.includes(permission);
}

/** Hide a block unless the signed-in persona holds the permission. */
export function RoleGate({
  user,
  permission,
  fallback = null,
  children,
}: {
  user: User;
  permission: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}) {
  return <>{can(user, permission) ? children : fallback}</>;
}
