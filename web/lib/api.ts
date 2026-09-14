import "server-only";

import { cookies } from "next/headers";

import type {
  CaseDetail,
  CaseList,
  CaseType,
  Comment,
  Metrics,
  User,
} from "./types";

const BASE = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
export const PERSONA_COOKIE = "persona";
/** Who you are before you pick a persona: a front-line analyst. */
export const DEFAULT_PERSONA = "usr_amelia";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function personaId(): Promise<string> {
  const store = await cookies();
  return store.get(PERSONA_COOKIE)?.value ?? DEFAULT_PERSONA;
}

/**
 * Single place the app talks to the case platform. Mock identity travels as a
 * header, so swapping in a real IdP later is a change to this function only.
 */
async function request<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const { json, ...rest } = init;
  const id = await personaId();
  const response = await fetch(`${BASE}${path}`, {
    ...rest,
    cache: "no-store",
    headers: {
      "X-User-Id": id,
      ...(json !== undefined ? { "Content-Type": "application/json" } : {}),
      ...rest.headers,
    },
    ...(json !== undefined ? { body: JSON.stringify(json) } : {}),
  });

  if (!response.ok) {
    const detail = await response
      .json()
      .then((body: { detail?: string }) => body.detail)
      .catch(() => undefined);
    throw new ApiError(response.status, detail ?? response.statusText);
  }
  return (await response.json()) as T;
}

export function getUsers(): Promise<User[]> {
  return request<User[]>("/api/users");
}

export function getCurrentUser(): Promise<User> {
  return request<User>("/api/me");
}

export function getCaseType(key: string): Promise<CaseType> {
  return request<CaseType>(`/api/case-types/${key}`);
}

export function getCaseTypes(): Promise<CaseType[]> {
  return request<CaseType[]>("/api/case-types");
}

export function getCases(
  key: string,
  params: Record<string, string | number | undefined>,
): Promise<CaseList> {
  const search = new URLSearchParams();
  for (const [name, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(name, String(value));
  }
  return request<CaseList>(`/api/case-types/${key}/cases?${search}`);
}

export function getMetrics(key: string): Promise<Metrics> {
  return request<Metrics>(`/api/case-types/${key}/metrics`);
}

export function getCase(id: string): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/cases/${id}`);
}

export function postTransition(
  id: string,
  body: { transition: string; note?: string; reason_code?: string },
): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/cases/${id}/transition`, {
    method: "POST",
    json: body,
  });
}

export function postComment(id: string, body: string): Promise<Comment> {
  return request<Comment>(`/api/cases/${id}/comments`, {
    method: "POST",
    json: { body },
  });
}

export function putAssignee(
  id: string,
  assignee_id: string | null,
): Promise<CaseDetail> {
  return request<CaseDetail>(`/api/cases/${id}/assignee`, {
    method: "POST",
    json: { assignee_id },
  });
}
