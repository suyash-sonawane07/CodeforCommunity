"""Deterministic service boundaries (Member C implements in Phases 2–3).

SCAFFOLD RULE: each service exposes typed inputs/outputs and raises
NotImplementedError. No algorithm values (weights, thresholds, distances,
costs, confidences) are hard-coded here — configuration objects are passed in
(brief §26). Routers (Member B) call these; swapping placeholders for real
logic must not touch routing code.
"""
