export type Fact = { label: string; value: React.ReactNode };

export function FactGrid({ facts }: { facts: Fact[] }) {
  return (
    <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {facts.map((fact) => (
        <div key={fact.label} className="min-w-0">
          <dt className="text-xs text-muted-foreground">{fact.label}</dt>
          <dd className="mt-0.5 text-sm">{fact.value}</dd>
        </div>
      ))}
    </dl>
  );
}
