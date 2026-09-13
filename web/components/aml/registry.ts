import type { EvidenceRegistry } from "@/components/kit/evidence-tabs";

import { CustomerEvidence } from "./customer-evidence";
import { RelatedCasesEvidence } from "./related-cases-evidence";
import { TransactionEvidence } from "./transaction-evidence";
import { WatchlistEvidence } from "./watchlist-evidence";

/** Maps the component names declared in `api/app/casetypes/aml.py` to React. */
export const AML_EVIDENCE: EvidenceRegistry = {
  TransactionEvidence,
  CustomerEvidence,
  WatchlistEvidence,
  RelatedCasesEvidence,
};
