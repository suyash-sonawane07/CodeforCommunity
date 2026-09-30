"use client";

import React, { useRef, useEffect } from "react";

const ROLES = [
  {
    id: "analyst",
    label: "Intelligence Analyst",
    badge: "Analyst",
    desc: "Inspect priority formula & cluster signals",
    color: "#1a73e8",
  },
  {
    id: "reviewer",
    label: "Independent Reviewer",
    badge: "Reviewer",
    desc: "Sign off flagged allocations under RBAC",
    color: "#e37400",
  },
  {
    id: "decision_maker",
    label: "Municipal Decision-Maker",
    badge: "Decision-Maker",
    desc: "Simulate budget policy & approve public capex",
    color: "#137333",
  },
  {
    id: "admin",
    label: "System Administrator",
    badge: "Admin",
    desc: "Full DPI infrastructure & audit access",
    color: "#b3261e",
  },
];

export function GoogleRoleAccountMenu({
  isOpen,
  onClose,
  activeRole,
  onSelectRole,
}: {
  isOpen: boolean;
  onClose: () => void;
  activeRole: string;
  onSelectRole: (role: string) => void;
}) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const currentRoleObj = ROLES.find((r) => r.id === activeRole) || ROLES[0];

  return (
    <div
      ref={menuRef}
      className="absolute right-0 top-12 z-50 w-84 rounded-3xl border border-[#dadce0] bg-white p-5 shadow-2xl ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150"
    >
      {/* Account Info Header */}
      <div className="flex flex-col items-center border-b border-[#edf2fa] pb-4 text-center">
        <div className="relative mb-2 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-tr from-[#1a73e8] via-[#8e24aa] to-[#ea4335] text-white text-xl font-bold shadow-md">
          {activeRole.charAt(0).toUpperCase()}
          <span className="absolute bottom-0 right-0 h-4 w-4 rounded-full border-2 border-white bg-[#34a853]" />
        </div>
        <h4 className="font-google font-bold text-sm text-[#1f1f1f]">
          CivicPulse Evaluator
        </h4>
        <p className="text-xs text-[#5f6368]">evaluator@civicpulse.gov.in</p>
        <span className="mt-2 rounded-full bg-[#d3e3fd] px-3 py-0.5 text-xs font-semibold text-[#041e49]">
          Role: {currentRoleObj.label}
        </span>
      </div>

      {/* Switch Roles Section */}
      <div className="mt-4">
        <p className="mb-2 text-[11px] font-bold uppercase tracking-wider text-[#747775]">
          Switch RBAC Evaluator Persona
        </p>
        <div className="space-y-1.5">
          {ROLES.map((role) => {
            const isSelected = activeRole === role.id;
            return (
              <button
                key={role.id}
                onClick={() => {
                  onSelectRole(role.id);
                  onClose();
                }}
                className={`flex w-full items-center justify-between rounded-2xl p-2.5 text-left transition ${
                  isSelected
                    ? "bg-[#e8f0fe] border border-[#1a73e8]/30"
                    : "hover:bg-[#f0f4f9] border border-transparent"
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: role.color }}
                    />
                    <span
                      className={`text-xs font-semibold ${
                        isSelected ? "text-[#1a73e8]" : "text-[#1f1f1f]"
                      }`}
                    >
                      {role.label}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#5f6368] pl-4">{role.desc}</p>
                </div>
                {isSelected && (
                  <span className="text-sm font-bold text-[#1a73e8]">✓</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 border-t border-[#edf2fa] pt-3 text-center text-[10px] text-[#747775]">
        RBAC policies enforced per FR-059 &amp; ISO 27001 audit standards
      </div>
    </div>
  );
}
