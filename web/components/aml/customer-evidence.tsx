import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FactGrid } from "@/components/kit/fact-grid";
import type { EvidenceProps } from "@/components/kit/evidence-tabs";
import { day, money, titleCase } from "@/lib/format";

export function CustomerEvidence({ detail }: EvidenceProps) {
  const customer = detail.subject;
  if (!customer) {
    return <p className="text-sm text-muted-foreground">No customer linked.</p>;
  }

  return (
    <div className="space-y-6">
      <FactGrid
        facts={[
          { label: "Legal name", value: customer.name },
          { label: "Type", value: titleCase(customer.kind) },
          { label: "Segment", value: customer.segment },
          { label: "Country", value: customer.country },
          { label: "Occupation / industry", value: customer.occupation },
          { label: "Onboarded", value: day(customer.onboarded_at) },
          { label: "KYC status", value: titleCase(customer.kyc_status) },
          {
            label: "Customer risk rating",
            value: titleCase(customer.risk_rating),
          },
          {
            label: "Lifetime volume",
            value: money(customer.lifetime_volume),
          },
          {
            label: "PEP",
            value: customer.is_pep ? (
              <Badge variant="destructive">Politically exposed</Badge>
            ) : (
              "No"
            ),
          },
          { label: "Contact", value: customer.email },
        ]}
      />

      <div>
        <h3 className="mb-2 text-sm font-medium">Accounts</h3>
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Account</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Opened</TableHead>
                <TableHead className="text-right">Balance</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {detail.accounts.map((account) => (
                <TableRow key={account.id}>
                  <TableCell className="font-mono text-xs">
                    {account.number}
                  </TableCell>
                  <TableCell>{titleCase(account.kind)}</TableCell>
                  <TableCell>{day(account.opened_at)}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {money(account.balance, true)}
                  </TableCell>
                  <TableCell>{titleCase(account.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
