import Link from "next/link";
import { Blocks } from "lucide-react";

import { Separator } from "@/components/ui/separator";
import type { CaseType, User } from "@/lib/types";
import { switchPersonaAction } from "@/app/actions";

import { NavLink } from "./nav-link";
import { PersonaSwitcher } from "./persona-switcher";

/**
 * Chrome shared by every app on the platform: navigation is generated from the
 * registered case types, identity from the mock persona switcher.
 */
export function AppShell({
  caseTypes,
  users,
  currentUser,
  children,
}: {
  caseTypes: CaseType[];
  users: User[];
  currentUser: User;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-full">
      <aside className="hidden w-64 shrink-0 flex-col gap-4 border-r bg-muted/30 p-3 md:flex">
        <Link href="/" className="flex items-center gap-2 px-2 pt-1">
          <span className="flex size-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Blocks className="size-4" />
          </span>
          <span className="text-sm leading-tight font-semibold">
            Northwind
            <span className="block text-xs font-normal text-muted-foreground">
              Internal case platform
            </span>
          </span>
        </Link>

        <Separator />

        <nav className="flex flex-col gap-0.5">
          <p className="px-2 py-1 text-xs font-medium text-muted-foreground">
            Apps
          </p>
          {caseTypes.map((caseType) => (
            <NavLink
              key={caseType.key}
              href={`/${caseType.key}`}
              icon={caseType.icon}
              label={caseType.plural_label}
              hint={`${caseType.sla_hours}h SLA`}
            />
          ))}
          <p className="mt-3 px-2 py-1 text-xs font-medium text-muted-foreground">
            Platform
          </p>
          <NavLink
            href="/platform"
            icon="Blocks"
            label="Building blocks"
            hint="Reusable across apps"
          />
        </nav>

        <div className="mt-auto">
          <Separator className="mb-2" />
          <PersonaSwitcher
            users={users}
            currentUser={currentUser}
            onSwitch={switchPersonaAction}
          />
        </div>
      </aside>

      <main className="min-w-0 flex-1">{children}</main>
    </div>
  );
}
