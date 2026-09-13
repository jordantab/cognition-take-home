import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { CaseDetail, EvidenceTab, State } from "@/lib/types";

export type EvidenceProps = { detail: CaseDetail; states: State[] };
export type EvidenceRegistry = Record<
  string,
  React.ComponentType<EvidenceProps>
>;

/**
 * The one place an app plugs its own domain UI into the platform: the case type
 * names a component per tab, the app registers it, everything else is generic.
 */
export function EvidenceTabs({
  tabs,
  registry,
  detail,
  states,
}: {
  tabs: EvidenceTab[];
  registry: EvidenceRegistry;
  detail: CaseDetail;
  states: State[];
}) {
  const usable = tabs.filter((tab) => tab.component in registry);
  if (usable.length === 0) return null;

  return (
    <Tabs defaultValue={usable[0].key}>
      <TabsList>
        {usable.map((tab) => (
          <TabsTrigger key={tab.key} value={tab.key}>
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {usable.map((tab) => {
        const Component = registry[tab.component];
        return (
          <TabsContent key={tab.key} value={tab.key} className="pt-4">
            <Component detail={detail} states={states} />
          </TabsContent>
        );
      })}
    </Tabs>
  );
}
