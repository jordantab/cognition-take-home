import { notFound } from "next/navigation";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AssigneePicker } from "@/components/kit/assignee-picker";
import { AuditTimeline } from "@/components/kit/audit-timeline";
import { CaseShell } from "@/components/kit/case-shell";
import { CommentThread } from "@/components/kit/comment-thread";
import { DecisionPanel } from "@/components/kit/decision-panel";
import { EvidenceTabs } from "@/components/kit/evidence-tabs";
import { SummaryList } from "@/components/kit/summary-list";
import {
  addCommentAction,
  applyTransitionAction,
  assignCaseAction,
} from "@/app/actions";
import {
  ApiError,
  getCase,
  getCaseType,
  getCurrentUser,
  getUsers,
} from "@/lib/api";
import { EVIDENCE_BY_CASE_TYPE } from "@/lib/registry";

export default async function CaseDetailPage({
  params,
}: PageProps<"/[caseType]/[caseId]">) {
  const { caseType, caseId } = await params;

  const detail = await getCase(caseId).catch((error) => {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  });
  if (detail.case.case_type !== caseType) notFound();

  const [config, users, currentUser] = await Promise.all([
    getCaseType(caseType),
    getUsers(),
    getCurrentUser(),
  ]);

  async function applyTransition(input: {
    transition: string;
    note?: string;
    reasonCode?: string;
  }) {
    "use server";
    return applyTransitionAction({ caseId, ...input });
  }

  async function addComment(body: string) {
    "use server";
    return addCommentAction({ caseId, body });
  }

  async function assign(assigneeId: string | null) {
    "use server";
    return assignCaseAction({ caseId, assigneeId });
  }

  return (
    <CaseShell
      caseRow={detail.case}
      states={config.states}
      backHref={`/${caseType}`}
      backLabel={`Back to ${config.plural_label.toLowerCase()}`}
      main={
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Why this alerted</CardTitle>
            </CardHeader>
            <CardContent>
              <SummaryList
                caseRow={detail.case}
                fields={config.summary_fields}
              />
            </CardContent>
          </Card>

          <EvidenceTabs
            tabs={config.evidence_tabs}
            registry={EVIDENCE_BY_CASE_TYPE[caseType] ?? {}}
            detail={detail}
            states={config.states}
          />

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Case notes</CardTitle>
            </CardHeader>
            <CardContent>
              <CommentThread
                comments={detail.comments}
                canComment={detail.can_comment}
                onSubmit={addComment}
              />
            </CardContent>
          </Card>
        </>
      }
      rail={
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Decision</CardTitle>
            </CardHeader>
            <CardContent>
              <DecisionPanel
                transitions={detail.available_transitions}
                onApply={applyTransition}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Owner</CardTitle>
            </CardHeader>
            <CardContent>
              <AssigneePicker
                users={users}
                value={detail.case.assignee?.id ?? null}
                disabled={
                  !detail.can_assign_others &&
                  detail.case.assignee?.id !== currentUser.id &&
                  detail.case.assignee != null
                }
                onAssign={assign}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Audit trail</CardTitle>
            </CardHeader>
            <CardContent>
              <AuditTimeline events={detail.events} states={config.states} />
            </CardContent>
          </Card>
        </>
      }
    />
  );
}
