import type { HTMLAttributes } from "react";

export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-lg border border-gray-200 bg-white p-4 shadow-sm ${className}`}
      {...props}
    />
  );
}

export function CardTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-gray-500">{children}</h3>
  );
}
