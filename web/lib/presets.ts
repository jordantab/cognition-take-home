import type { Preset } from "./types";

/**
 * The saved view a queue opens on when the URL carries no `preset`. A case type
 * can point a role at a different view, so an approver does not land on the
 * empty personal queue that makes sense for an analyst.
 */
export function defaultPreset(
  presets: Preset[],
  role: string,
): Preset | undefined {
  return (
    presets.find((preset) => preset.default_for_roles.includes(role)) ??
    presets.find((preset) => preset.default) ??
    presets[0]
  );
}

/**
 * Query params a saved view expands to. `mine` resolves to `me` rather than an
 * id so the view follows the persona switcher instead of whoever clicked it.
 */
export function presetParams(preset: Preset | undefined): Record<string, string> {
  if (!preset) return {};
  const params: Record<string, string> = { ...preset.filters };
  if (preset.mine) {
    params.assignee_id = "me";
    params.open_only = "true";
  }
  return params;
}
