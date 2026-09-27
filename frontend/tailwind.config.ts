import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Civic, public-sector palette (clarity over decoration — PRD §8.2)
        civic: {
          50: "#f0f7ff",
          100: "#dcecff",
          500: "#2563eb",
          600: "#1d4ed8",
          700: "#1e40af",
          900: "#1e3a5f",
        },
      },
    },
  },
  plugins: [],
};
export default config;
