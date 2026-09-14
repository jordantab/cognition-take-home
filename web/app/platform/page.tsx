import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/kit/page-header";
import { blocksWithSizes, caseTypeSource } from "@/lib/blocks";
import { getCaseTypes } from "@/lib/api";

export default async function PlatformPage() {
  const [blocks, caseTypes, amlSource] = await Promise.all([
    blocksWithSizes(),
    getCaseTypes(),
    caseTypeSource("aml"),
  ]);

  const shared = blocks.filter((block) => block.layer === "platform");
  const appSpecific = blocks.filter((block) => block.layer === "app");
  const sharedLines = shared.reduce((sum, block) => sum + block.lines, 0);
  const appLines = appSpecific.reduce((sum, block) => sum + block.lines, 0);
  const reusePct = Math.round((sharedLines / (sharedLines + appLines)) * 100);

  return (
    <div className="flex flex-col">
      <PageHeader
        title="Platform building blocks"
        description="Every screen in this prototype is composed from these blocks. A new internal app is a case-type declaration plus its evidence components."
      />

      <div className="space-y-6 p-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <Stat
            label="Shared platform blocks"
            value={`${shared.length}`}
            hint={`${sharedLines} lines, reused by every app`}
          />
          <Stat
            label="AML-specific blocks"
            value={`${appSpecific.length}`}
            hint={`${appLines} lines written for this app only`}
          />
          <Stat
            label="Reused"
            value={`${reusePct}%`}
            hint="of the UI in the AML app comes from the kit"
          />
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">
              Registered apps ({caseTypes.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {caseTypes.map((caseType) => (
              <div key={caseType.key} className="text-sm">
                <span className="font-medium">{caseType.label}</span>
                <span className="text-muted-foreground">
                  {" "}
                  — {caseType.states.length} states,{" "}
                  {caseType.transitions.length} transitions,{" "}
                  {caseType.columns.length} queue columns,{" "}
                  {caseType.evidence_tabs.length} evidence tabs, all declared
                  server-side.
                </span>
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="grid gap-4 md:grid-cols-2">
          {blocks.map((block) => (
            <Card key={block.name} className="gap-2">
              <CardHeader>
                <CardTitle className="flex items-center justify-between gap-2 text-sm">
                  <span className="font-mono">{block.name}</span>
                  <Badge
                    variant={
                      block.layer === "platform" ? "secondary" : "outline"
                    }
                  >
                    {block.layer === "platform" ? "Shared" : "AML only"}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {block.description}
                </p>
                <p className="mt-2 font-mono text-xs text-muted-foreground">
                  web/{block.file} · {block.lines} lines
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {amlSource ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">
                api/app/casetypes/aml.py — the whole AML app definition
              </CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="max-h-[28rem] overflow-auto rounded-lg bg-muted p-4 text-xs leading-relaxed">
                <code>{amlSource}</code>
              </pre>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <Card className="gap-1">
      <CardContent>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="mt-1 text-3xl font-semibold tabular-nums">{value}</p>
        <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
      </CardContent>
    </Card>
  );
}
