"use client";

import { Check, ChevronsUpDown } from "lucide-react";
import { useTransition } from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { User } from "@/lib/types";

import { UserChip } from "./user-chip";

/**
 * Mock identity. Every request carries the selected user, so permissions,
 * "assigned to me" views and four-eyes controls are demonstrable in one click.
 */
export function PersonaSwitcher({
  users,
  currentUser,
  onSwitch,
}: {
  users: User[];
  currentUser: User;
  onSwitch: (userId: string) => Promise<void>;
}) {
  const [pending, startTransition] = useTransition();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          disabled={pending}
          className="h-auto w-full justify-between px-2 py-1.5"
        >
          <UserChip
            user={currentUser}
            subtitle={currentUser.role_label}
            size="md"
          />
          <ChevronsUpDown className="size-4 text-muted-foreground" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-64">
        <DropdownMenuLabel>Sign in as</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {users.map((user) => (
          <DropdownMenuItem
            key={user.id}
            onSelect={() => startTransition(() => onSwitch(user.id))}
          >
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="truncate text-sm">{user.name}</span>
              <span className="truncate text-xs text-muted-foreground">
                {user.job_title} · {user.role_label}
              </span>
            </span>
            {user.id === currentUser.id ? <Check className="size-4" /> : null}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
