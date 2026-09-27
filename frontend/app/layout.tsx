import type { Metadata } from "next";

import { AppShell } from "@/components/layouts";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "CivicPulse",
    template: "%s — CivicPulse",
  },
  description:
    "AI development-needs intelligence layer for citizen requests (hackathon scaffold — features not yet implemented).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
