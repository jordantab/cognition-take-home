"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "cn";

import { Icon } from "./icon";

export function NavLink({
  href,
  icon,
  label,
  hint,
}: {
  href: string;
  icon: string;
  label: string;
  hint?: string;
}) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(`${href}/`);

  return (
    <Link
      href={href}
      className={cn(
        "flex items-start gap-2.5 rounded-md px-2 py-2 text-sm transition-colors",
        active
          ? "bg-secondary font-medium text-secondary-foreground"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
    >
      <Icon name={icon} className="mt-0.5 size-4 shrink-0" />
      <span className="min-w-0">
        <span className="block truncate">{label}</span>
        {hint ? (
          <span className="block truncate text-xs text-muted-foreground">
            {hint}
          </span>
        ) : null}
      </span>
    </Link>
  );
}
