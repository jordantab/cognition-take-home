import { cn } from "cn";
import { Flag } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { EvidenceProps } from "@/components/kit/evidence-tabs";
import { dateTime, money, titleCase } from "@/lib/format";

export function TransactionEvidence({ detail }: EvidenceProps) {
  const flagged = new Set<string>(
    (detail.case.extra?.transaction_ids as string[] | undefined) ?? [],
  );
  const flaggedTotal = detail.transactions
    .filter((transaction) => flagged.has(transaction.id))
    .reduce((sum, transaction) => sum + transaction.amount, 0);

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        {flagged.size} flagged transactions totalling {money(flaggedTotal, true)}
        , shown against the customer&apos;s recent activity.
      </p>
      <div className="overflow-hidden rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-40">Posted</TableHead>
              <TableHead className="w-28 text-right">Amount</TableHead>
              <TableHead className="w-24">Direction</TableHead>
              <TableHead className="w-28">Channel</TableHead>
              <TableHead>Counterparty</TableHead>
              <TableHead className="w-16">Country</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {detail.transactions.map((transaction) => (
              <TableRow
                key={transaction.id}
                className={cn(
                  flagged.has(transaction.id) &&
                    "bg-amber-50/60 dark:bg-amber-950/20",
                )}
              >
                <TableCell className="whitespace-nowrap">
                  <span className="flex items-center gap-1.5">
                    {flagged.has(transaction.id) ? (
                      <Flag className="size-3 text-amber-600" />
                    ) : null}
                    {dateTime(transaction.posted_at)}
                  </span>
                </TableCell>
                <TableCell className="text-right tabular-nums">
                  {money(transaction.amount, true)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={
                      transaction.direction === "credit"
                        ? "text-emerald-700 dark:text-emerald-300"
                        : "text-slate-700 dark:text-slate-300"
                    }
                  >
                    {transaction.direction === "credit" ? "In" : "Out"}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {titleCase(transaction.channel)}
                </TableCell>
                <TableCell className="max-w-56 truncate">
                  {transaction.counterparty_name}
                  <span className="block truncate text-xs text-muted-foreground">
                    {transaction.description}
                  </span>
                </TableCell>
                <TableCell className="font-mono text-xs">
                  {transaction.counterparty_country}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
