export function EmptyState({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-gray-300 p-10 text-center">
      <p className="text-sm font-medium text-gray-700">{title}</p>
      {description ? <p className="max-w-sm text-xs text-gray-500">{description}</p> : null}
      {children}
    </div>
  );
}
