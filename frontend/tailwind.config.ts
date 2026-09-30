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
      fontFamily: {
        sans: [
          "Google Sans",
          "Inter",
          "Roboto",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        google: ["Google Sans", "Product Sans", "sans-serif"],
      },
      colors: {
        // Civic, public-sector palette (preserved for compatibility)
        civic: {
          50: "#f0f7ff",
          100: "#dcecff",
          500: "#2563eb",
          600: "#1a73e8",
          700: "#1557bf",
          900: "#1e3a5f",
        },
        // Official Google & Material Design 3 Palette
        google: {
          blue: {
            DEFAULT: "#1a73e8",
            50: "#f0f7ff",
            100: "#e8f0fe",
            200: "#d2e3fc",
            500: "#1a73e8",
            600: "#1967d2",
            700: "#185abc",
            800: "#174ea6",
            m3: "#0b57d0",
            container: "#d3e3fd",
            onContainer: "#041e49",
          },
          red: {
            DEFAULT: "#ea4335",
            50: "#fce8e6",
            100: "#fad2cf",
            500: "#ea4335",
            600: "#d93025",
            700: "#c5221f",
            m3: "#ba1a1a",
            container: "#f9dedc",
            onContainer: "#410002",
          },
          yellow: {
            DEFAULT: "#fbbc04",
            50: "#fef7e0",
            100: "#feefc3",
            500: "#fbbc04",
            600: "#f9ab00",
            700: "#f29900",
            800: "#ea8600",
            container: "#fef7da",
            onContainer: "#523600",
          },
          green: {
            DEFAULT: "#34a853",
            50: "#e6f4ea",
            100: "#ceead6",
            500: "#34a853",
            600: "#1e8e3e",
            700: "#188038",
            container: "#c4eed0",
            onContainer: "#072711",
          },
          grey: {
            50: "#f8f9fa",
            100: "#f1f3f4",
            200: "#e8eaed",
            300: "#dadce0",
            400: "#bdc1c6",
            500: "#9aa0a6",
            600: "#80868b",
            700: "#5f6368",
            800: "#3c4043",
            900: "#202124",
          },
          surface: {
            DEFAULT: "#f8fafd",
            low: "#f0f4f9",
            card: "#ffffff",
            high: "#e9eef6",
            highest: "#dfe4ea",
          },
        },
      },
      boxShadow: {
        "google-sm": "0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15)",
        "google-md": "0 1px 3px 0 rgba(60, 64, 67, 0.3), 0 4px 8px 3px rgba(60, 64, 67, 0.15)",
        "google-lg": "0 2px 6px 2px rgba(60, 64, 67, 0.15), 0 8px 12px 4px rgba(60, 64, 67, 0.15)",
        "google-fab": "0 4px 8px 3px rgba(60, 64, 67, 0.15), 0 1px 3px 0 rgba(60, 64, 67, 0.3)",
      },
    },
  },
  plugins: [],
};

export default config;
