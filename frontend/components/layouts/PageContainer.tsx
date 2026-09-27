/** Standard content container for pages rendered inside AppShell. */
export function PageContainer({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto w-full max-w-3xl">{children}</div>;
}
