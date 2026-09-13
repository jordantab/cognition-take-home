import { cn } from "cn";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { User } from "@/lib/types";

export function UserChip({
  user,
  subtitle,
  className,
  size = "sm",
}: {
  user: User | null | undefined;
  subtitle?: string;
  className?: string;
  size?: "sm" | "md";
}) {
  if (!user) {
    return (
      <span className={cn("text-sm text-muted-foreground", className)}>
        Unassigned
      </span>
    );
  }
  return (
    <span className={cn("flex min-w-0 items-center gap-2", className)}>
      <Avatar className={size === "md" ? "size-8" : "size-6"}>
        <AvatarFallback className="text-[10px] font-medium">
          {user.initials}
        </AvatarFallback>
      </Avatar>
      <span className="min-w-0">
        <span className="block truncate text-sm">{user.name}</span>
        {subtitle ? (
          <span className="block truncate text-xs text-muted-foreground">
            {subtitle}
          </span>
        ) : null}
      </span>
    </span>
  );
}
