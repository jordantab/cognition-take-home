"use client";

import { useTransition } from "react";
import { toast } from "sonner";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { User } from "@/lib/types";
import type { ActionResult } from "@/app/actions";

const UNASSIGNED = "__unassigned__";

/** Only offers the changes the current role is actually allowed to make. */
export function AssigneePicker({
  users,
  value,
  assignableUserIds,
  canUnassign,
  lockReason,
  onAssign,
}: {
  users: User[];
  value: string | null;
  assignableUserIds: string[];
  canUnassign: boolean;
  lockReason: string;
  onAssign: (assigneeId: string | null) => Promise<ActionResult>;
}) {
  const [pending, startTransition] = useTransition();
  const options = users.filter((user) => assignableUserIds.includes(user.id));
  const locked = options.length === 0;

  if (locked) {
    const owner = users.find((user) => user.id === value);
    return (
      <div className="space-y-1">
        <p className="text-sm">{owner ? owner.name : "Unassigned"}</p>
        <p className="text-xs text-muted-foreground">{lockReason}</p>
      </div>
    );
  }

  return (
    <Select
      value={value ?? UNASSIGNED}
      disabled={pending}
      onValueChange={(next) =>
        startTransition(async () => {
          const result = await onAssign(next === UNASSIGNED ? null : next);
          if (result.ok) toast.success("Owner updated");
          else toast.error(result.error);
        })
      }
    >
      <SelectTrigger size="sm" className="w-full">
        <SelectValue placeholder="Unassigned" />
      </SelectTrigger>
      <SelectContent>
        {canUnassign || value === null ? (
          <SelectItem value={UNASSIGNED}>Unassigned</SelectItem>
        ) : null}
        {options.map((user) => (
          <SelectItem key={user.id} value={user.id}>
            {user.name} · {user.role_label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
