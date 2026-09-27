/** Tiny shared formatting helpers (kept dependency-free). */

export function formatCount(n: number): string {
  return new Intl.NumberFormat("en-IN").format(n);
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}
