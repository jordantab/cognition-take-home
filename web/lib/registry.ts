import { AML_EVIDENCE } from "@/components/aml/registry";
import type { EvidenceRegistry } from "@/components/kit/evidence-tabs";

/**
 * Case type key -> its evidence components. This is the whole per-app frontend
 * wiring; routes, queue, filters, workflow and audit UI are shared.
 */
export const EVIDENCE_BY_CASE_TYPE: Record<string, EvidenceRegistry> = {
  aml: AML_EVIDENCE,
};
