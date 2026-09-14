"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useTransition } from "react";

/** Shared URL-state helper: filters, sort and paging live in the query string. */
export function useQueueParams() {
  const params = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  const setParams = useCallback(
    (next: Record<string, string | null>, { reset = false } = {}) => {
      const search = new URLSearchParams(reset ? "" : params.toString());
      for (const [key, value] of Object.entries(next)) {
        if (value === null || value === "") search.delete(key);
        else search.set(key, value);
      }
      if (!("page" in next)) search.delete("page");
      const query = search.toString();
      startTransition(() => {
        router.replace(query ? `${pathname}?${query}` : pathname, {
          scroll: false,
        });
      });
    },
    [params, pathname, router],
  );

  return { params, setParams, pending };
}
