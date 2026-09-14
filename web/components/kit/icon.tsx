import {
  Blocks,
  FileText,
  LayoutDashboard,
  ScanFace,
  ShieldAlert,
  Wallet,
  type LucideIcon,
} from "lucide-react";

/** Case types name their icon in config; the platform resolves it. */
const ICONS: Record<string, LucideIcon> = {
  ShieldAlert,
  ScanFace,
  Wallet,
  FileText,
  Blocks,
  LayoutDashboard,
};

export function Icon({
  name,
  className,
}: {
  name: string;
  className?: string;
}) {
  const Component = ICONS[name] ?? FileText;
  return <Component className={className} />;
}
