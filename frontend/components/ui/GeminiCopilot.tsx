"use client";

import React, { useState } from "react";
import { GeminiSparkleIcon } from "./GoogleIcons";

interface Message {
  sender: "user" | "gemini";
  text: string;
  timestamp: string;
}

const PRESET_PROMPTS = [
  "Explain the DPI Priority Formula & Factor Weights",
  "Summarize evidence for Paithan Water Crisis (#1)",
  "How does anti-astroturfing protect democratic voice?",
  "Simulate allocating ₹30M to Rural Transit Hubs",
];

const PRESET_ANSWERS: Record<string, string> = {
  "Explain the DPI Priority Formula & Factor Weights":
    "The CivicPulse Priority Score is calculated deterministically via:\n\n**`score = wd·d + wg·g + wi·i + we·e - wf·f`**\n\n• **wd (0.35)**: Independent citizen demand count (deduplicated across dialects).\n• **wg (0.25)**: Infrastructure deficit gap score relative to municipal standards.\n• **wi (0.20)**: Public health, safety, and economic impact score.\n• **we (0.15)**: Social vulnerability & marginalized community equity index.\n• **wf (0.05)**: Anti-astroturfing penalty for coordinate repetitions & bot blast patterns.\n\nEvery factor is fully auditable and published transparently under FR-057.",

  "Summarize evidence for Paithan Water Crisis (#1)":
    "**Paithan Rural Hub (Cluster #1) Analysis:**\n\n• **Severity Score**: 84.5 / 100\n• **Independent Citizen Demand**: 342 verified individuals across Marathi (72%) and Hindi (21%) voice & text reports.\n• **Semantic Convergence**: 94.2% coherence detailing dried canal valves and delayed water tankers.\n• **Existing Infrastructure**: Paithan Main Treatment Plant running at 142% overload.\n• **Recommended Intervention**: 4.5km ductile iron feeder line (Est. Capex ₹4.5 Cr).",

  "How does anti-astroturfing protect democratic voice?":
    "CivicPulse enforces strict separation between **`raw_message_count`** and **`independent_demand_count`** (FR-024).\n\n1. **Semantic Embeddings**: Clusters detect copy-pasted campaign text and identical spam scripts.\n2. **Geodesic Coordinate Jitter Analysis**: Prevents bot-farms from spoofing identical GPS coordinates.\n3. **Rate-Limiting & Penalty**: Bot blasts incur the **`wf·f`** astroturf penalty, preventing wealthy interest groups from drowning out underserved rural communities.",

  "Simulate allocating ₹30M to Rural Transit Hubs":
    "**What-If Simulation Output (FR-056 Non-Binding):**\n\n• **Target Sector**: Rural Transit & Mobility\n• **Allocated Budget**: ₹30,000,000\n• **Estimated Beneficiaries**: 58,000 citizens across 4 clusters\n• **Coverage Increase**: +19.4% in high-deficit rural corridors\n• **Equity Index Gain**: +0.14 across Shirur and Paithan blocks.",
};

export function GeminiCopilot({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "gemini",
      text: "Hello! I am **CivicPulse Gemini Copilot**, your explainable AI assistant for Digital Public Infrastructure. Ask me about cluster rankings, spatial evidence, or policy simulations.",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (userText: string) => {
    if (!userText.trim()) return;

    const newMsg: Message = {
      sender: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, newMsg]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      let answer = PRESET_ANSWERS[userText];
      if (!answer) {
        answer = `CivicPulse Gemini analyzed "${userText}":\n\nBased on BRICS geospatial indicators and verified citizen demand, this query maps to cross-sector infrastructure gap analysis. The DPI intelligence pipeline confirms explainable evidence across Maharashtra, Rio de Janeiro, and Gauteng pilot zones.`;
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: "gemini",
          text: answer,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
      setIsTyping(false);
    }, 600);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30 backdrop-blur-sm transition-opacity">
      <div className="flex h-full w-full max-w-lg flex-col bg-white shadow-2xl transition-transform">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#e0e3e7] bg-[#f8fafd] px-5 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#1a73e8] via-[#8e24aa] to-[#ea4335] text-white shadow-md shadow-blue-500/20">
              <GeminiSparkleIcon className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="font-google text-base font-bold text-[#1f1f1f]">
                  CivicPulse <span className="gemini-text font-extrabold">Gemini</span>
                </h3>
                <span className="rounded-full bg-[#d3e3fd] px-2 py-0.5 text-[10px] font-semibold text-[#041e49]">
                  Flash 2.0
                </span>
              </div>
              <p className="text-xs text-[#5f6368]">
                Explainable DPI Intelligence Copilot
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full text-[#5f6368] hover:bg-[#e8eaed] transition"
            aria-label="Close Gemini Copilot"
          >
            ✕
          </button>
        </div>

        {/* Preset Prompt Pills */}
        <div className="border-b border-[#edf2fa] bg-[#ffffff] p-3 overflow-x-auto">
          <p className="mb-2 text-[11px] font-bold uppercase tracking-wider text-[#747775]">
            Quick Explorations
          </p>
          <div className="flex gap-2 overflow-x-auto pb-1 text-xs">
            {PRESET_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSend(prompt)}
                className="shrink-0 rounded-full border border-[#dadce0] bg-[#f8f9fa] px-3 py-1.5 text-xs text-[#3c4043] hover:border-[#1a73e8] hover:bg-[#e8f0fe] hover:text-[#1a73e8] transition"
              >
                ✨ {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 space-y-4 overflow-y-auto p-5 text-sm">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${
                m.sender === "user" ? "items-end" : "items-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                  m.sender === "user"
                    ? "rounded-br-none bg-[#0b57d0] text-white"
                    : "rounded-bl-none border border-[#e0e3e7] bg-[#f8fafd] text-[#1f1f1f]"
                }`}
              >
                <div className="whitespace-pre-line leading-relaxed text-xs sm:text-sm">
                  {m.text}
                </div>
              </div>
              <span className="mt-1 text-[10px] text-[#747775]">{m.timestamp}</span>
            </div>
          ))}

          {isTyping && (
            <div className="flex items-center gap-2 text-xs text-[#5f6368]">
              <span className="h-2 w-2 rounded-full bg-[#1a73e8] animate-bounce" />
              <span className="h-2 w-2 rounded-full bg-[#ea4335] animate-bounce [animation-delay:0.2s]" />
              <span className="h-2 w-2 rounded-full bg-[#34a853] animate-bounce [animation-delay:0.4s]" />
              <span>Gemini is generating explainable insights...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="border-t border-[#e0e3e7] bg-white p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="flex items-center gap-2 rounded-full border border-[#dadce0] bg-[#f8f9fa] px-4 py-2 focus-within:border-[#1a73e8] focus-within:bg-white focus-within:shadow-md transition"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Gemini about DPI clusters, formulas, or policy..."
              className="flex-1 bg-transparent text-sm text-[#1f1f1f] placeholder-[#747775] outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0b57d0] text-white disabled:opacity-40 transition hover:bg-[#0842a0]"
            >
              ➤
            </button>
          </form>
          <p className="mt-2 text-center text-[10px] text-[#747775]">
            Gemini provides explainable DPI suggestions. Human officials make all final allocation decisions.
          </p>
        </div>
      </div>
    </div>
  );
}
