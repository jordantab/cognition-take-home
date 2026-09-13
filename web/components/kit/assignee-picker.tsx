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

export function AssigneePicker({
  users,
  value,
  disabled,
  onAssign,
}: {
  users: User[];
  value: string | null;
  disabled?: boolean;
  onAssign: (assigneeId: string | null) => Promise<ActionResult>;
}) {
  const [pending, startTransition] = useTransition();

  return (
    <Select
      value={value ?? UNASSIGNED}
      disabled={disabled || pending}
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
        <SelectItem value={UNASSIGNED}>Unassigned</SelectItem>
        {users.map((user) => (
          <SelectItem key={user.id} value={user.id}>
            {user.name} · {user.role_label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
