"use client";

import { Search, X } from "lucide-react";
import { useState } from "react";
import { cn } from "cn";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { defaultPreset, presetParams } from "@/lib/presets";
import type { Filter, Preset } from "@/lib/types";

import { useQueueParams } from "./use-queue-params";

const ALL = "__all__";

/**
 * Filters and saved views rendered straight from the case type declaration.
 * A new app declares filters server-side and gets this UI for free.
 */
export function FilterBar({
  filters,
  presets,
  currentUserId,
  currentUserRole,
}: {
  filters: Filter[];
  presets: Preset[];
  currentUserId: string;
  currentUserRole: string;
}) {
  const { params, setParams } = useQueueParams();
  const search = filters.find((filter) => filter.type === "search");
  const selects = filters.filter((filter) => filter.type !== "search");
  const activePreset =
    params.get("preset") ?? defaultPreset(presets, currentUserRole)?.key;

  const query = params.get("q") ?? "";
  const [term, setTerm] = useState(query);
  const [lastQuery, setLastQuery] = useState(query);
  if (query !== lastQuery) {
    setLastQuery(query);
    setTerm(query);
  }

  function applyPreset(preset: Preset) {
    const next: Record<string, string | null> = {
      preset: preset.key,
      status: null,
      priority: null,
      typology: null,
      assignee_id: null,
      open_only: null,
    };
    for (const [key, value] of Object.entries(presetParams(preset))) {
      next[key] = value;
    }
    setParams(next, { reset: true });
  }

  const hasFilters =
    selects.some((filter) => params.get(filter.key)) || params.get("q") !== null;

  function selectValue(key: string): string {
    const value = params.get(key);
    if (!value) return ALL;
    return key === "assignee_id" && value === "me" ? currentUserId : value;
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-1">
        {presets.map((preset) => (
          <button
            key={preset.key}
            type="button"
            onClick={() => applyPreset(preset)}
            className={cn(
              "rounded-md px-2.5 py-1.5 text-sm transition-colors",
              activePreset === preset.key
                ? "bg-secondary font-medium text-secondary-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {search ? (
          <form
            className="relative w-64"
            onSubmit={(event) => {
              event.preventDefault();
              setParams({ q: term || null });
            }}
          >
            <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={term}
              onChange={(event) => setTerm(event.target.value)}
              onBlur={() => setParams({ q: term || null })}
              placeholder={search.placeholder}
              className="pl-8"
              aria-label={search.label}
            />
          </form>
        ) : null}

        {selects.map((filter) => (
          <Select
            key={filter.key}
            value={selectValue(filter.key)}
            onValueChange={(value) =>
              setParams({ [filter.key]: value === ALL ? null : value })
            }
          >
            <SelectTrigger size="sm" className="w-auto min-w-36">
              <SelectValue placeholder={filter.label} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={ALL}>All {filter.label.toLowerCase()}</SelectItem>
              {filter.key === "assignee_id" ? (
                <SelectItem value="unassigned">Unassigned</SelectItem>
              ) : null}
              {filter.options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ))}

        {hasFilters ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setParams({}, { reset: true })}
          >
            <X className="size-3.5" />
            Clear
          </Button>
        ) : null}
      </div>
    </div>
  );
}
