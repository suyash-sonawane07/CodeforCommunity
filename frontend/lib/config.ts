/**
 * Central environment configuration.
 *
 * RULE: `NEXT_PUBLIC_API_BASE_URL` is the ONE place the backend URL lives.
 * Never hardcode localhost or URLs elsewhere (scaffold requirement §5).
 */
export const API_BASE_URL: string = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const APP_NAME = "CivicPulse";
export const APP_VERSION = "0.1.0";

/**
 * Runtime guard: fail loudly in development if the API base URL is unset so
 * misconfiguration surfaces immediately, not in a broken fetch.
 */
export function assertApiConfigured(): void {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL && process.env.NODE_ENV === "development") {
    // eslint-disable-next-line no-console
    console.warn(
      "[civicpulse] NEXT_PUBLIC_API_BASE_URL is not set — falling back to " + API_BASE_URL,
    );
  }
}
