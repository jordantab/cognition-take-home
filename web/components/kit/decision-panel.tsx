"use client";

import { Lock } from "lucide-react";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { AvailableTransition } from "@/lib/types";
import type { ActionResult } from "@/app/actions";

type Variant = "default" | "secondary" | "destructive" | "outline" | "ghost";

/**
 * Decisioning UI generated from the workflow: buttons, required notes, reason
 * codes and the four-eyes lock all come from the server's declaration.
 */
export function DecisionPanel({
  transitions,
  onApply,
}: {
  transitions: AvailableTransition[];
  onApply: (input: {
    transition: string;
    note?: string;
    reasonCode?: string;
  }) => Promise<ActionResult>;
}) {
  const [active, setActive] = useState<AvailableTransition | null>(null);
  const [note, setNote] = useState("");
  const [reasonCode, setReasonCode] = useState("");
  const [pending, startTransition] = useTransition();

  function start(transition: AvailableTransition) {
    if (transition.requires_note || transition.requires_reason_code) {
      setNote("");
      setReasonCode("");
      setActive(transition);
      return;
    }
    submit(transition);
  }

  function submit(transition: AvailableTransition, payload?: {
    note?: string;
    reasonCode?: string;
  }) {
    startTransition(async () => {
      const result = await onApply({
        transition: transition.key,
        ...payload,
      });
      if (result.ok) {
        setActive(null);
        toast.success(`${transition.label} applied`);
      } else {
        toast.error(result.error);
      }
    });
  }

  if (transitions.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No actions available from this status.
      </p>
    );
  }

  const blocked = !active
    ? false
    : (active.requires_note && !note.trim()) ||
      (active.requires_reason_code && !reasonCode);

  return (
    <>
      <div className="flex flex-col gap-2">
        {transitions.map((transition) =>
          transition.enabled ? (
            <Button
              key={transition.key}
              variant={transition.variant as Variant}
              onClick={() => start(transition)}
              disabled={pending}
              className="justify-start"
            >
              {transition.label}
            </Button>
          ) : (
            <Tooltip key={transition.key}>
              <TooltipTrigger asChild>
                <span className="inline-flex">
                  <Button
                    variant="outline"
                    disabled
                    className="w-full justify-start"
                  >
                    <Lock className="size-3.5" />
                    {transition.label}
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent className="max-w-64">
                {transition.disabled_reason}
              </TooltipContent>
            </Tooltip>
          ),
        )}
      </div>

      <Dialog
        open={active !== null}
        onOpenChange={(open) => !open && setActive(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{active?.label}</DialogTitle>
            <DialogDescription>
              {active?.description ||
                "This decision is written to the case audit trail."}
            </DialogDescription>
          </DialogHeader>

          {active?.requires_reason_code ? (
            <div className="flex flex-col gap-2">
              <Label htmlFor="reason">Reason code</Label>
              <Select value={reasonCode} onValueChange={setReasonCode}>
                <SelectTrigger id="reason" className="w-full">
                  <SelectValue placeholder="Select a reason" />
                </SelectTrigger>
                <SelectContent>
                  {active.reason_codes.map((reason) => (
                    <SelectItem key={reason.key} value={reason.key}>
                      {reason.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : null}

          {active?.requires_note ? (
            <div className="flex flex-col gap-2">
              <Label htmlFor="note">Rationale</Label>
              <Textarea
                id="note"
                rows={4}
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="What did you find, and why is this the right call?"
              />
            </div>
          ) : null}

          <DialogFooter>
            <Button variant="ghost" onClick={() => setActive(null)}>
              Cancel
            </Button>
            <Button
              variant={(active?.variant as Variant) ?? "default"}
              disabled={blocked || pending}
              onClick={() =>
                active &&
                submit(active, {
                  note: note.trim() || undefined,
                  reasonCode: reasonCode || undefined,
                })
              }
            >
              {pending ? "Saving..." : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
