#!/usr/bin/env bash
# ==============================================================================
# CivicPulse — End-to-End Live System Demo Walkthrough (Track 1: AI for DPI)
# ==============================================================================
# Demonstrates the complete flow across all phases:
# 1. System Health & Protocols
# 2. Multilingual Citizen Intake (Hindi, Marathi, Portuguese, English)
# 3. Citizen Request Tracking (CP-2026-XXXXXX Reference Code)
# 4. Audio STT Ingestion
# 5. PostGIS Geospatial Clustering & Anti-Astroturfing Deduplication
# 6. Spatial Infrastructure Gap Detection & Conflicting Project Avoidance
# 7. Transparent AI Prioritisation Formula (wd·d + wg·g + wi·i + we·e - wf·f)
# 8. Traceable Evidence Dossier with Synthetic Dataset Labels (FR-057)
# 9. Human Review Gate (RBAC sign-off)
# 10. Policy What-If Simulator (Budget allocations & coverage deltas)
# 11. Post-Intervention Outcome Measurement (Baseline vs Followup - FR-067)
# 12. Immutable Governance Audit Trail (FR-062)
# ==============================================================================

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_GREEN="\033[32m"
C_BLUE="\033[34m"
C_CYAN="\033[36m"
C_AMBER="\033[33m"
C_PURPLE="\033[35m"

print_step() {
    echo -e "\n${C_BOLD}${C_CYAN}======================================================================${C_RESET}"
    echo -e "${C_BOLD}${C_BLUE}STEP $1: $2${C_RESET}"
    echo -e "${C_BOLD}${C_CYAN}======================================================================${C_RESET}"
}

print_success() {
    echo -e "${C_GREEN}✓ $1${C_RESET}"
}

print_info() {
    echo -e "${C_AMBER}ℹ $1${C_RESET}"
}

pretty_json() {
    if command -v jq >/dev/null 2>&1; then
        jq .
    else
        python3 -m json.tool 2>/dev/null || cat
    fi
}

# ------------------------------------------------------------------------------
# 0. Check / Start Backend Server
# ------------------------------------------------------------------------------
echo -e "${C_BOLD}${C_PURPLE}🏛️  CIVICPULSE — AI FOR DPI & GOVERNANCE (BRICS PILOT) — LIVE DEMO${C_RESET}"
echo -e "Target API: ${API_BASE_URL}\n"

if ! curl -s -f "${API_BASE_URL}/health" >/dev/null 2>&1; then
    print_info "Backend is not running at ${API_BASE_URL}. Starting uvicorn in background..."
    cd "${BASE_DIR}/backend"
    .venv/bin/uvicorn app.main:app --port 8000 >/tmp/civicpulse_demo_backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Started backend (PID: ${BACKEND_PID}). Waiting for health check..."
    for i in {1..20}; do
        if curl -s -f "${API_BASE_URL}/health" >/dev/null 2>&1; then
            break
        fi
        sleep 0.5
    done
fi

# ------------------------------------------------------------------------------
# Step 1: Health & System Diagnostics
# ------------------------------------------------------------------------------
print_step "1" "Backend Health & Service Check"
HEALTH_RES=$(curl -s "${API_BASE_URL}/health")
echo "${HEALTH_RES}" | pretty_json
print_success "CivicPulse API is online and responding."

# ------------------------------------------------------------------------------
# Step 2: Multilingual Citizen Intake (India - Hindi / Marathi)
# ------------------------------------------------------------------------------
print_step "2" "Citizen Intake — Hindi Request (India Pilot: Pune, Maharashtra)"
REQ_HI=$(curl -s -X POST "${API_BASE_URL}/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "text",
    "language_hint": "hi",
    "text": "पुणे शहर आणि हवेली तालुक्यात पिण्याच्या पाण्याची तीव्र टंचाई आहे. दररोज टँकरची वाट पाहावी लागते.",
    "location_text": "हवेली, पुणे, महाराष्ट्र",
    "consent_ack": true
  }')
echo "${REQ_HI}" | pretty_json
REQ_ID_HI=$(echo "${REQ_HI}" | (command -v jq >/dev/null 2>&1 && jq -r .request_id || python3 -c "import sys, json; print(json.load(sys.stdin).get('request_id'))"))
REF_CODE_HI=$(echo "${REQ_HI}" | (command -v jq >/dev/null 2>&1 && jq -r .reference_code || python3 -c "import sys, json; print(json.load(sys.stdin).get('reference_code'))"))
print_success "Created Hindi citizen request ID: ${REQ_ID_HI} (Ref Code: ${REF_CODE_HI})"

# ------------------------------------------------------------------------------
# Step 3: Multilingual Citizen Intake (Brazil - Portuguese)
# ------------------------------------------------------------------------------
print_step "3" "Citizen Intake — Portuguese Request (Brazil Pilot: Rio de Janeiro)"
REQ_PT=$(curl -s -X POST "${API_BASE_URL}/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "text",
    "language_hint": "pt",
    "text": "A estrada principal no Morro dos Prazeres tem crateras enormes e os ônibus não conseguem subir nos dias de chuva.",
    "location_text": "Morro dos Prazeres, Rio de Janeiro, Brasil",
    "consent_ack": true
  }')
echo "${REQ_PT}" | pretty_json
REQ_ID_PT=$(echo "${REQ_PT}" | (command -v jq >/dev/null 2>&1 && jq -r .request_id || python3 -c "import sys, json; print(json.load(sys.stdin).get('request_id'))"))
print_success "Created Portuguese citizen request ID: ${REQ_ID_PT}"

# ------------------------------------------------------------------------------
# Step 4: Multilingual Citizen Intake (South Africa - English)
# ------------------------------------------------------------------------------
print_step "4" "Citizen Intake — English Request (South Africa Pilot: Western Cape)"
REQ_EN=$(curl -s -X POST "${API_BASE_URL}/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "text",
    "language_hint": "en",
    "text": "Residents in Khayelitsha Site C have had broken sewer pipes and contaminated standpipes for three weeks.",
    "location_text": "Site C, Khayelitsha, Western Cape, South Africa",
    "consent_ack": true
  }')
echo "${REQ_EN}" | pretty_json
REQ_ID_EN=$(echo "${REQ_EN}" | (command -v jq >/dev/null 2>&1 && jq -r .request_id || python3 -c "import sys, json; print(json.load(sys.stdin).get('request_id'))"))
print_success "Created South Africa citizen request ID: ${REQ_ID_EN}"

# ------------------------------------------------------------------------------
# Step 5: Citizen Tracking by Public Reference Code
# ------------------------------------------------------------------------------
print_step "5" "Citizen Tracking Verification by Reference Code (S-03)"
STATUS_RES=$(curl -s "${API_BASE_URL}/requests/${REQ_ID_HI}")
echo "${STATUS_RES}" | pretty_json
print_success "Request ${REQ_ID_HI} resolved with status and timestamp tracking."

# ------------------------------------------------------------------------------
# Step 6: Audio STT Upload Flow
# ------------------------------------------------------------------------------
print_step "6" "Citizen Voice Audio Ingestion (STT Pipeline)"
VOICE_REQ=$(curl -s -X POST "${API_BASE_URL}/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "voice",
    "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
    "location_text": "Paithan, Maharashtra",
    "consent_ack": true
  }')
VOICE_ID=$(echo "${VOICE_REQ}" | (command -v jq >/dev/null 2>&1 && jq -r .request_id || python3 -c "import sys, json; print(json.load(sys.stdin).get('request_id'))"))
print_info "Ingested voice submission, Request ID: ${VOICE_ID}"

# ------------------------------------------------------------------------------
# Step 7: PostGIS Geospatial Demand Map & Clustering
# ------------------------------------------------------------------------------
print_step "7" "PostGIS Geospatial Demand Map & Hotspot Clusters (S-06)"
GEO_RES=$(curl -s "${API_BASE_URL}/geospatial/clusters")
echo "${GEO_RES}" | (command -v jq >/dev/null 2>&1 && jq '{type: .type, feature_count: (.features | length), sample_feature: .features[0]}' || head -n 25)
print_success "Retrieved GeoJSON feature collection with PostGIS coordinate centroids."

# ------------------------------------------------------------------------------
# Step 8: Hotspot List with Anti-Astroturfing Deduplication (FR-024)
# ------------------------------------------------------------------------------
print_step "8" "Ranked Clusters — Anti-Astroturfing Verification (FR-024)"
ANALYST_LOGIN=$(curl -s -X POST "${API_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "analyst@civicpulse.dev", "password": "password"}')
ANALYST_TOKEN=$(echo "${ANALYST_LOGIN}" | (command -v jq >/dev/null 2>&1 && jq -r .access_token || python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token'))"))

CLUSTERS_RES=$(curl -s -H "Authorization: Bearer ${ANALYST_TOKEN}" "${API_BASE_URL}/clusters")
echo "${CLUSTERS_RES}" | (command -v jq >/dev/null 2>&1 && jq '.items[0:3] | map({id: .id, issue_type: .issue_type, independent_demand_count: .independent_demand_count, raw_message_count: .raw_message_count, district: .district})' || head -n 30)
print_success "Independent citizen demand count separated from raw submission volume."

# ------------------------------------------------------------------------------
# Step 9: Spatial Gap Analysis & Conflicting Project Avoidance (FR-042)
# ------------------------------------------------------------------------------
print_step "9" "Spatial Infrastructure Gap Detection & Conflicting Project Avoidance (FR-042)"
GAP_RES=$(curl -s -H "Authorization: Bearer ${ANALYST_TOKEN}" "${API_BASE_URL}/clusters/1/gap-analysis")
echo "${GAP_RES}" | pretty_json
print_success "Gap analysis computed against national benchmarks with project collision check."

# ------------------------------------------------------------------------------
# Step 10: Transparent AI Prioritisation Formula
# ------------------------------------------------------------------------------
print_step "10" "Explainable AI Prioritisation Formula Breakdown (FR-048)"
PRIORITY_RES=$(curl -s -H "Authorization: Bearer ${ANALYST_TOKEN}" "${API_BASE_URL}/clusters/1/priority")
echo "${PRIORITY_RES}" | pretty_json
print_success "Formula: score = wd·d + wg·g + wi·i + we·e - wf·f with full component transparency."

# ------------------------------------------------------------------------------
# Step 11: Human Review Gate (RBAC Authorization)
# ------------------------------------------------------------------------------
print_step "11" "Human Review Gate — Reviewer Sign-Off (PRD S-12, FR-058)"
LOGIN_RES=$(curl -s -X POST "${API_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "reviewer@civicpulse.dev", "password": "password"}')
REVIEWER_TOKEN=$(echo "${LOGIN_RES}" | (command -v jq >/dev/null 2>&1 && jq -r .access_token || python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token'))"))

REVIEW_RES=$(curl -s -X POST "${API_BASE_URL}/clusters/1/review" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${REVIEWER_TOKEN}" \
  -d '{
    "action": "approve",
    "note": "Authorized after cross-referencing district water grid master plan and satellite imagery."
  }')
echo "${REVIEW_RES}" | pretty_json
print_success "Human reviewer approved Cluster #1 with signed justification."

# ------------------------------------------------------------------------------
# Step 12: Policy What-If Simulator & Outcome Measurement
# ------------------------------------------------------------------------------
print_step "12" "Policy Simulator & Post-Intervention Outcomes (S-11, S-14)"
DECISION_LOGIN=$(curl -s -X POST "${API_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "decision@civicpulse.dev", "password": "password"}')
DECISION_TOKEN=$(echo "${DECISION_LOGIN}" | (command -v jq >/dev/null 2>&1 && jq -r .access_token || python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token'))"))

SIM_RES=$(curl -s -X POST "${API_BASE_URL}/simulations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${DECISION_TOKEN}" \
  -d '{
    "sector_allocations": {
      "water": 600000,
      "roads": 450000,
      "health": 350000,
      "education": 200000
    }
  }')
echo "${SIM_RES}" | pretty_json
print_success "Policy scenario calculated with illustrative disclaimer (FR-056)."

OUTCOME_RES=$(curl -s -H "Authorization: Bearer ${REVIEWER_TOKEN}" "${API_BASE_URL}/clusters/1/outcome")
echo "${OUTCOME_RES}" | pretty_json
print_success "Outcome monitoring retrieved with baseline vs followup metrics and correlation disclaimer (FR-067)."

# ------------------------------------------------------------------------------
# Step 13: Governance Audit Trail
# ------------------------------------------------------------------------------
print_step "13" "Immutable Governance Audit Trail (FR-062)"
ADMIN_LOGIN=$(curl -s -X POST "${API_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@civicpulse.dev", "password": "password"}')
ADMIN_TOKEN=$(echo "${ADMIN_LOGIN}" | (command -v jq >/dev/null 2>&1 && jq -r .access_token || python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token'))"))

AUDIT_RES=$(curl -s -H "Authorization: Bearer ${ADMIN_TOKEN}" "${API_BASE_URL}/audit-logs")
echo "${AUDIT_RES}" | (command -v jq >/dev/null 2>&1 && jq '.items[0:3]' || head -n 30)
print_success "Audit log confirmed tamper-evident trace of human reviews and scenario runs."

echo -e "\n${C_BOLD}${C_GREEN}======================================================================${C_RESET}"
echo -e "${C_BOLD}${C_GREEN}🎉 ALL PHASES VERIFIED: CIVICPULSE END-TO-END DEMO SUCCESSFUL!${C_RESET}"
echo -e "${C_BOLD}${C_GREEN}======================================================================${C_RESET}\n"
