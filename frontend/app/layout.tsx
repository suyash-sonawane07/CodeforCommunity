import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layouts";

const googleFont = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CivicPulse — Google DPI Intelligence Layer",
  description: "AI development-needs intelligence layer translating citizen voice requests into transparent infrastructure investments.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={googleFont.className}>
      <body className="bg-[#f8fafd] text-[#1f1f1f] antialiased font-sans selection:bg-[#d3e3fd] selection:text-[#041e49]">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}


