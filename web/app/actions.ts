"use server";

import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";

import {
  ApiError,
  PERSONA_COOKIE,
  postComment,
  postTransition,
  putAssignee,
} from "@/lib/api";

export type ActionResult = { ok: true } | { ok: false; error: string };

async function run(work: () => Promise<unknown>): Promise<ActionResult> {
  try {
    await work();
    revalidatePath("/", "layout");
    return { ok: true };
  } catch (error) {
    if (error instanceof ApiError) return { ok: false, error: error.message };
    throw error;
  }
}

export async function applyTransitionAction(input: {
  caseId: string;
  transition: string;
  note?: string;
  reasonCode?: string;
}): Promise<ActionResult> {
  return run(() =>
    postTransition(input.caseId, {
      transition: input.transition,
      note: input.note,
      reason_code: input.reasonCode,
    }),
  );
}

export async function addCommentAction(input: {
  caseId: string;
  body: string;
}): Promise<ActionResult> {
  return run(() => postComment(input.caseId, input.body));
}

export async function assignCaseAction(input: {
  caseId: string;
  assigneeId: string | null;
}): Promise<ActionResult> {
  return run(() => putAssignee(input.caseId, input.assigneeId));
}

export async function switchPersonaAction(userId: string): Promise<void> {
  const store = await cookies();
  store.set(PERSONA_COOKIE, userId, { path: "/", sameSite: "lax" });
  revalidatePath("/", "layout");
}
