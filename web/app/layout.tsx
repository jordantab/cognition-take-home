import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppShell } from "@/components/kit/app-shell";
import { getCaseTypes, getCurrentUser, getUsers } from "@/lib/api";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Northwind internal case platform",
  description:
    "AML investigation queue built on a reusable internal case platform.",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const [caseTypes, users, currentUser] = await Promise.all([
    getCaseTypes(),
    getUsers(),
    getCurrentUser(),
  ]);

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <TooltipProvider delayDuration={200}>
          <AppShell
            caseTypes={caseTypes}
            users={users}
            currentUser={currentUser}
          >
            {children}
          </AppShell>
        </TooltipProvider>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
