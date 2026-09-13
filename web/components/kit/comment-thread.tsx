"use client";

import { useState, useTransition } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { Comment } from "@/lib/types";
import { dateTime, relative } from "@/lib/format";
import type { ActionResult } from "@/app/actions";

import { UserChip } from "./user-chip";

export function CommentThread({
  comments,
  canComment,
  onSubmit,
}: {
  comments: Comment[];
  canComment: boolean;
  onSubmit: (body: string) => Promise<ActionResult>;
}) {
  const [body, setBody] = useState("");
  const [pending, startTransition] = useTransition();

  function submit() {
    const text = body.trim();
    if (!text) return;
    startTransition(async () => {
      const result = await onSubmit(text);
      if (result.ok) {
        setBody("");
        toast.success("Comment added");
      } else {
        toast.error(result.error);
      }
    });
  }

  return (
    <div className="flex flex-col gap-4">
      {comments.length === 0 ? (
        <p className="text-sm text-muted-foreground">No comments yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {comments.map((comment) => (
            <li key={comment.id} className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2">
                <UserChip user={comment.author} />
                <span
                  className="text-xs text-muted-foreground"
                  title={dateTime(comment.created_at)}
                >
                  {relative(comment.created_at)}
                </span>
              </div>
              <p className="pl-8 text-sm">{comment.body}</p>
            </li>
          ))}
        </ul>
      )}

      {canComment ? (
        <div className="flex flex-col items-end gap-2">
          <Textarea
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder="Add a note for the case file..."
            rows={3}
          />
          <Button size="sm" onClick={submit} disabled={pending || !body.trim()}>
            {pending ? "Posting..." : "Comment"}
          </Button>
        </div>
      ) : (
        <p className="text-xs text-muted-foreground">
          Your role has read-only access to this thread.
        </p>
      )}
    </div>
  );
}
