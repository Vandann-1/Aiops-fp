"""
Generates Technical Diagrams 08 to 14 for the AIOps Service Desk Capstone Report.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from diagram_utils import create_canvas, draw_card, draw_arrow, save_diagram, THEMES, BG_WHITE, TEXT_NAVY, TEXT_MUTED

OUTPUT_DIR = "Project Report/Diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# DIAGRAM 08: Local AI Runbook Retrieval — TF-IDF + Cosine Similarity
# ==============================================================================
def generate_diagram_08():
    fig, ax = create_canvas(
        title="Local AI Runbook Retrieval — TF-IDF + Cosine Similarity",
        subtitle="Mathematical Vector Space Model: Explainable, Deterministic & Air-Gapped NLP Architecture"
    )

    # Top Tag Banner: NO EXTERNAL AI
    no_ai_box = patches.FancyBboxPatch((400, 720), 800, 36, boxstyle="round,pad=0,rounding_size=8",
                                       facecolor="#EFF6FF", edgecolor="#2563EB", linewidth=1.4, zorder=2)
    ax.add_patch(no_ai_box)
    ax.text(800, 738, "100% LOCAL NLP • scikit-learn TF-IDF • COSINE SIMILARITY • ZERO EXTERNAL AI APIS", 
            fontsize=9.5, fontweight='bold', color="#1D4ED8", ha='center', va='center', zorder=3)

    # Branch 1: Incident Query (Left)
    draw_card(ax, 70, 560, 400, 135, "INPUT BRANCH A: INCIDENT TICKET", [
        "Title: 'Web server returns 502 Bad Gateway'",
        "Description: 'Nginx service inactive after deploy'",
        "Category: SERVER",
        "Indicative Symptoms extracted from description"
    ], theme="blue", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 270, 560, 270, 485, color="#2563EB", lw=1.6)

    draw_card(ax, 70, 410, 400, 75, "TEXT PREPARATION & TOKENIZATION", [
        "Lowercasing, regex token extraction, punctuation removal",
        "Stop-word filtering (English standard stop-words)"
    ], theme="blue", corner_radius=10, align='left', title_size=9.5, body_size=8)

    draw_arrow(ax, 270, 410, 270, 335, color="#2563EB", lw=1.6)

    draw_card(ax, 70, 260, 400, 75, "TF-IDF QUERY VECTORIZATION", [
        "Term Frequency * Inverse Document Frequency",
        "Yields normalized query vector Q = [w_1, w_2, ..., w_n]"
    ], theme="blue", corner_radius=10, align='left', title_size=9.5, body_size=8)

    # Branch 2: Runbook Knowledge Base (Right)
    draw_card(ax, 1130, 560, 400, 135, "INPUT BRANCH B: RUNBOOK KNOWLEDGE BASE", [
        "Active SOP Corpus (12 Canonical Runbooks)",
        "Title: 'Restart Nginx Web Server' (RB-0001)",
        "Description & Procedural Steps",
        "Multi-line Indicative Symptoms & Category"
    ], theme="green", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 1330, 560, 1330, 485, color="#16A34A", lw=1.6)

    draw_card(ax, 1130, 410, 400, 75, "CORPUS PREPROCESSING & VOCABULARY", [
        "Document concatenation (Title + Desc + Symptoms)",
        "Global vocabulary matrix construction (N features)"
    ], theme="green", corner_radius=10, align='left', title_size=9.5, body_size=8)

    draw_arrow(ax, 1330, 410, 1330, 335, color="#16A34A", lw=1.6)

    draw_card(ax, 1130, 260, 400, 75, "RUNBOOK DOCUMENT VECTORS", [
        "Sparse matrix representation for all active runbooks",
        "Yields document vectors D_i = [w_i1, w_i2, ..., w_in]"
    ], theme="green", corner_radius=10, align='left', title_size=9.5, body_size=8)

    # Central Convergence: Dot Product & Cosine Similarity
    draw_arrow(ax, 470, 297, 570, 297, color="#2563EB", lw=2)
    draw_arrow(ax, 1130, 297, 1030, 297, color="#16A34A", lw=2)

    draw_card(ax, 570, 230, 460, 135, "COSINE SIMILARITY ENGINE", [
        "Formula: Cosine_Sim(Q, D_i) = (Q · D_i) / (||Q|| * ||D_i||)",
        "Computes linear angle dot product between vectors",
        "Ranks all active runbooks by descending similarity score",
        "Execution latency: < 10 ms (In-memory scikit-learn)"
    ], theme="dark", corner_radius=12, align='center', title_size=11, body_size=8.5)

    # Arrow down to Threshold Cutoff
    draw_arrow(ax, 800, 230, 800, 175, color="#2563EB", lw=2)

    # Bottom Row: Threshold Filtering & Citation Results
    draw_card(ax, 80, 80, 420, 85, "THRESHOLD FILTER GATE", [
        "Configurable minimum match threshold: score >= 0.20",
        "If score < 0.20: No recommendation returned",
        "Guarantees protection against irrelevant matches"
    ], theme="orange", corner_radius=10, align='left', title_size=9.5, body_size=8)

    draw_arrow(ax, 500, 122, 590, 122, color="#EA580C", lw=1.8)

    draw_card(ax, 590, 80, 460, 85, "RECOMMENDED RUNBOOK", [
        "Selected: RB-0001 (Restart Nginx Web Server)",
        "Confidence Score: 0.7450 (74.50% match)",
        "Attached to Incident via RunbookRecommendation"
    ], theme="green", badge="MATCH >= 0.20", corner_radius=10, align='left', title_size=9.5, body_size=8)

    draw_arrow(ax, 1050, 122, 1140, 122, color="#16A34A", lw=1.8)

    draw_card(ax, 1140, 80, 390, 85, "VERIFIABLE CITATION EVIDENCE", [
        "Matched Symptoms: 'Nginx service inactive', '502'",
        "Cited Steps: Exact procedural steps from SOP",
        "100% transparent auditability for operator"
    ], theme="blue", badge="EXPLAINABILITY", corner_radius=10, align='left', title_size=9.5, body_size=8)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "08_AI_NLP_TFIDF_Architecture.png"))


# ==============================================================================
# DIAGRAM 09: Human Approval and Safe Automation Control
# ==============================================================================
def generate_diagram_09():
    fig, ax = create_canvas(
        title="Human Approval and Safe Automation Control Flow",
        subtitle="Multi-Tiered Safety Gates: Diagnostic Checklist, Dry-Run Simulation, and Verification"
    )

    # 3 Pillar Badges at Top
    p1 = patches.FancyBboxPatch((80, 715), 440, 40, boxstyle="round,pad=0,rounding_size=8",
                                facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.4, zorder=2)
    ax.add_patch(p1)
    ax.text(300, 735, "1. AI RECOMMENDS (Explainable Advice)", fontsize=10, fontweight='bold', color="#1D4ED8", ha='center', va='center')

    p2 = patches.FancyBboxPatch((580, 715), 440, 40, boxstyle="round,pad=0,rounding_size=8",
                                facecolor="#FFF7ED", edgecolor="#F97316", linewidth=1.4, zorder=2)
    ax.add_patch(p2)
    ax.text(800, 735, "2. ADMIN APPROVES (Mandatory Human Gate)", fontsize=10, fontweight='bold', color="#C2410C", ha='center', va='center')

    p3 = patches.FancyBboxPatch((1080, 715), 440, 40, boxstyle="round,pad=0,rounding_size=8",
                                facecolor="#F0FDF4", edgecolor="#22C55E", linewidth=1.4, zorder=2)
    ax.add_patch(p3)
    ax.text(1300, 735, "3. SYSTEM EXECUTES ONLY ALLOWED ACTIONS", fontsize=10, fontweight='bold', color="#15803D", ha='center', va='center')

    # Top Flow: Recommendation -> Request Approval -> Review
    draw_card(ax, 80, 580, 360, 95, "AI RUNBOOK RECOMMENDATION", [
        "Generated via local TF-IDF match",
        "Runbook: RB-0001 (Restart Nginx)",
        "Includes citation & evidence metadata"
    ], theme="blue", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 440, 627, 520, 627, color="#2563EB", lw=1.8)

    draw_card(ax, 520, 580, 360, 95, "APPROVAL REQUEST SUBMITTED", [
        "Created by IT Admin in admin portal",
        "AutomationApproval entity created",
        "Incident transitions to PENDING_APPROVAL"
    ], theme="orange", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 880, 627, 960, 627, color="#EA580C", lw=1.8)

    draw_card(ax, 960, 580, 360, 95, "READ-ONLY DRY-RUN INSPECTION", [
        "Displays expected simulation output",
        "Evaluates reversibility & rollback plan",
        "Zero database or OS state mutation"
    ], theme="orange", badge="READ ONLY", corner_radius=10, align='left', title_size=10, body_size=8.5)

    # Down from Dry-Run to Human Decision Diamond
    draw_arrow(ax, 1140, 580, 1140, 500, color="#EA580C", lw=2)

    dec = patches.RegularPolygon((1140, 450), numVertices=4, radius=42, orientation=0,
                                 facecolor="#FFF7ED", edgecolor="#F97316", linewidth=1.6, zorder=2)
    ax.add_patch(dec)
    ax.text(1140, 450, "HUMAN\nDECISION", fontsize=8.5, fontweight='bold', color="#C2410C", ha='center', va='center', zorder=3)

    # Reject Branch (Right)
    draw_arrow(ax, 1182, 450, 1260, 450, label="REJECT", color="#DC2626", lw=1.8, label_color="#DC2626")
    draw_card(ax, 1260, 405, 270, 90, "REJECTION RECORDED", [
        "Mandatory rejection reason logged",
        "Incident marked as REJECTED",
        "Logged to AuditLog & Activity",
        "Automated execution STOPPED"
    ], theme="red", corner_radius=8, align='left', title_size=9, body_size=8)

    # Approve Branch (Left into 7-Point Safety Checklist)
    draw_arrow(ax, 1098, 450, 970, 450, label="APPROVE", color="#16A34A", lw=2, label_color="#166534")

    # Middle Box: 7-Point Pre-Automation Diagnostic Checklist
    draw_card(ax, 540, 310, 430, 225, "7-POINT PRE-AUTOMATION DIAGNOSTIC CHECKLIST", [
        "1. Runbook Attached: Incident has recommended runbook",
        "2. Runbook Active: Runbook is active in catalog",
        "3. Action Exists: Associated script hook is defined",
        "4. Allowlist Valid: Action is in SAFE_ACTIONS allowlist",
        "5. Incident Open: Target ticket is not already resolved",
        "6. Approval Granted: Status is explicitly APPROVED",
        "7. Simulation Safe: Strictly in-process Python callable"
    ], theme="green", badge="ALL 7 MUST PASS", corner_radius=12, align='left', title_size=10, body_size=8)

    # Down from Checklist to Controlled Executor
    draw_arrow(ax, 540, 420, 450, 420, color="#16A34A", lw=2)

    draw_card(ax, 80, 350, 370, 140, "CONTROLLED SIMULATION EXECUTOR", [
        "Strict SAFE_ACTIONS allowlist lookup",
        "Zero OS subprocesses / Zero shell commands",
        "Pure Python callable function simulation",
        "Idempotency Guard: Blocks duplicate execution",
        "Output captured: 'Nginx restart simulated successfully'"
    ], theme="green", badge="SIMULATION MODE", corner_radius=12, align='left', title_size=10, body_size=8)

    # Down to Verification Gate
    draw_arrow(ax, 265, 350, 265, 245, color="#16A34A", lw=2)

    draw_card(ax, 80, 160, 370, 85, "POST-EXECUTION HEALTH VERIFICATION", [
        "Simulated diagnostic health check",
        "Evaluates whether service recovered",
        "Crucial safety gate before ticket closure"
    ], theme="blue", corner_radius=10, align='left', title_size=10, body_size=8.5)

    # Branch from Verification: Failed vs Passed
    draw_arrow(ax, 450, 202, 550, 202, label="PASSED", color="#16A34A", lw=2, label_color="#166534")
    draw_card(ax, 550, 160, 410, 85, "AUTOMATED RESOLUTION", [
        "Incident status transitions to RESOLVED",
        "resolved_at UTC timestamp recorded for MTTR",
        "Employee 1 to 5 star feedback form unlocked"
    ], theme="green", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 265, 160, 265, 120, color="#DC2626", lw=1.6)
    draw_card(ax, 80, 65, 370, 55, "VERIFICATION FAILED -> TICKET REMAINS OPEN", [
        "Error recorded in AuditLog; Manual engineer takeover required"
    ], theme="red", corner_radius=8, align='center', title_size=8.5, body_size=7.5)

    # Bottom Statement Banner
    bot_box = patches.FancyBboxPatch((550, 65), 980, 55, boxstyle="round,pad=0,rounding_size=10",
                                     facecolor="#F8FAFC", edgecolor="#DC2626", linewidth=1.4, zorder=2)
    ax.add_patch(bot_box)
    ax.text(1040, 92, "CORE SAFETY GUARANTEE: EXECUTION SUCCESS ≠ INCIDENT RESOLUTION", 
            fontsize=10.5, fontweight='bold', color="#991B1B", ha='center', va='center', zorder=3)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "09_Safety_Human_Approval_Flow.png"))


# ==============================================================================
# DIAGRAM 10: ER Database Diagram
# ==============================================================================
def generate_diagram_10():
    fig, ax = create_canvas(
        title="Entity Relationship (ER) Schema Diagram",
        subtitle="Relational Data Architecture: 9 Entities, Constraints, Keys, and Referential Integrity"
    )

    # Table drawing helper
    def draw_entity_table(x, y, w, title, fields, theme="blue"):
        th = 26 + len(fields) * 16.5 + 8
        draw_card(ax, x, y, w, th, title, theme=theme, corner_radius=8, title_size=9.5)
        # Table Header Line
        line = plt.Line2D([x + 4, x + w - 4], [y + th - 24, y + th - 24], color=THEMES[theme]["border"], linewidth=1)
        ax.add_line(line)
        fy = y + th - 38
        for ftype, fname, fextra in fields:
            ax.text(x + 10, fy, ftype, fontsize=7.5, fontweight='bold', color="#2563EB" if ftype == "PK" else ("#DC2626" if ftype == "FK" else "#64748B"), family='monospace')
            ax.text(x + 38, fy, fname, fontsize=8, color=TEXT_NAVY, family='sans-serif')
            ax.text(x + w - 10, fy, fextra, fontsize=7.5, color="#64748B", family='monospace', ha='right')
            fy -= 16.5
        return th

    # 1. User
    draw_entity_table(70, 580, 240, "auth_user (User)", [
        ("PK", "id", "BigAuto"),
        ("  ", "username", "Char(150)"),
        ("  ", "email", "Char(254)"),
        ("  ", "role", "Char(20)")
    ], theme="gray")

    # 2. Incident
    draw_entity_table(380, 480, 290, "incidents_incident", [
        ("PK", "id", "BigAuto"),
        ("  ", "incident_number", "Char(20) [UQ]"),
        ("  ", "title", "Char(200)"),
        ("  ", "description", "Text"),
        ("  ", "category", "Char(20)"),
        ("  ", "priority", "Char(20)"),
        ("  ", "status", "Char(25)"),
        ("  ", "intent", "Char(50)"),
        ("  ", "service", "Char(50)"),
        ("FK", "created_by_id", "User.id"),
        ("  ", "created_at", "DateTime")
    ], theme="blue")

    # 3. Runbook
    draw_entity_table(760, 500, 290, "runbooks_runbook", [
        ("PK", "id", "BigAuto"),
        ("  ", "runbook_number", "Char(20) [UQ]"),
        ("  ", "title", "Char(200)"),
        ("  ", "category", "Char(20)"),
        ("  ", "symptoms", "Text"),
        ("  ", "steps", "Text"),
        ("  ", "risk_level", "Char(20)"),
        ("  ", "automation_action", "Char(100)"),
        ("  ", "is_active", "Boolean"),
        ("FK", "created_by_id", "User.id")
    ], theme="green")

    # 4. RunbookRecommendation
    draw_entity_table(1140, 520, 310, "runbooks_runbookrecommendation", [
        ("PK", "id", "BigAuto"),
        ("FK", "incident_id", "Incident.id [1:1]"),
        ("FK", "runbook_id", "Runbook.id [M:1]"),
        ("  ", "match_score", "Float"),
        ("  ", "citation_metadata", "JSONField"),
        ("  ", "created_at", "DateTime")
    ], theme="green")

    # 5. AutomationApproval
    draw_entity_table(380, 200, 290, "automation_automationapproval", [
        ("PK", "id", "BigAuto"),
        ("FK", "incident_id", "Incident.id [M:1]"),
        ("FK", "runbook_id", "Runbook.id [M:1]"),
        ("FK", "requested_by_id", "User.id"),
        ("FK", "reviewed_by_id", "User.id"),
        ("  ", "status", "Char(20)"),
        ("  ", "reason", "Text"),
        ("  ", "created_at", "DateTime")
    ], theme="orange")

    # 6. AutomationExecution
    draw_entity_table(760, 230, 290, "automation_automationexecution", [
        ("PK", "id", "BigAuto"),
        ("FK", "approval_id", "Approval.id [1:1]"),
        ("  ", "action_name", "Char(100)"),
        ("  ", "status", "Char(20)"),
        ("  ", "output", "Text"),
        ("  ", "error_message", "Text"),
        ("  ", "completed_at", "DateTime")
    ], theme="orange")

    # 7. VerificationResult
    draw_entity_table(1140, 250, 310, "automation_verificationresult", [
        ("PK", "id", "BigAuto"),
        ("FK", "execution_id", "Execution.id [1:1]"),
        ("  ", "status", "Char(20) [PASSED/FAILED]"),
        ("  ", "message", "Text"),
        ("FK", "checked_by_id", "User.id"),
        ("  ", "checked_at", "DateTime")
    ], theme="blue")

    # 8. AuditLog
    draw_entity_table(70, 260, 240, "automation_auditlog", [
        ("PK", "id", "BigAuto"),
        ("FK", "incident_id", "Incident.id"),
        ("FK", "actor_id", "User.id"),
        ("  ", "event_type", "Char(50)"),
        ("  ", "message", "Text"),
        ("  ", "metadata", "JSONField"),
        ("  ", "created_at", "DateTime")
    ], theme="purple")

    # 9. IncidentFeedback
    draw_entity_table(70, 70, 240, "incidents_incidentfeedback", [
        ("PK", "id", "BigAuto"),
        ("FK", "incident_id", "Incident.id [1:1]"),
        ("FK", "user_id", "User.id"),
        ("  ", "rating", "Integer (1-5)"),
        ("  ", "comment", "Text"),
        ("  ", "created_at", "DateTime")
    ], theme="purple")

    # Relationships & Connectors
    # User -> Incident
    draw_arrow(ax, 310, 630, 380, 630, label="1:N", color="#3B82F6", lw=1.4)
    # Incident -> Recommendation
    draw_arrow(ax, 670, 610, 1140, 610, label="1:1", color="#22C55E", lw=1.4)
    # Runbook -> Recommendation
    draw_arrow(ax, 1050, 610, 1140, 610, label="1:N", color="#22C55E", lw=1.4)
    # Incident -> Approval
    draw_arrow(ax, 525, 480, 525, 360, label="1:N", color="#F97316", lw=1.4)
    # Approval -> Execution
    draw_arrow(ax, 670, 280, 760, 280, label="1:1", color="#F97316", lw=1.4)
    # Execution -> Verification
    draw_arrow(ax, 1050, 290, 1140, 290, label="1:1", color="#3B82F6", lw=1.4)
    # Incident -> Feedback
    draw_arrow(ax, 400, 480, 220, 175, label="1:1", color="#A855F7", lw=1.2, ls="--")
    # Incident -> AuditLog
    draw_arrow(ax, 380, 520, 310, 380, label="1:N", color="#A855F7", lw=1.2, ls="--")

    save_diagram(fig, os.path.join(OUTPUT_DIR, "10_ER_Database_Diagram.png"))


# ==============================================================================
# DIAGRAM 11: Testing Strategy Diagram
# ==============================================================================
def generate_diagram_11():
    fig, ax = create_canvas(
        title="AIOps Service Desk Comprehensive Testing Strategy",
        subtitle="Quality Assurance Hierarchy: 120 Automated Tests Across 5 Architectural Verification Tiers"
    )

    tiers = [
        # (Tier Title, Badge, Description, Items, Theme, Width, Y)
        ("TIER 5 — END-TO-END WORKFLOW TESTING", "8 TESTS", "Full lifecycle test: Ingestion -> Local AI Retrieval -> Approval Gate -> Mock Exec -> Verification -> Feedback", 
         ["Verifies state machine transitions across all 9 statuses", "Validates automated resolution strictly conditional on verification", "Confirms operator feedback loop updating telemetry"], 
         "purple", 700, 620),

        ("TIER 4 — FAILURE & ROBUSTNESS TESTING (Phase 15)", "17 TESTS", "Rigorous edge-case and failure scenario validation across all apps", 
         ["Empty descriptions & unicode text resilience", "Sub-threshold retrieval gracefully handling non-matches (< 0.20)", "Unapproved, rejected, or unlisted action execution blocking", "Double approval & duplicate feedback prevention"], 
         "red", 880, 490),

        ("TIER 3 — SECURITY & ACCESS CONTROL TESTING", "15 TESTS", "Persona boundary enforcement, CSRF, and allowlist protection", 
         ["Role-based access decorators (@employee_required, @it_admin_required)", "Object-level ownership query filtering (cross-tenant protection)", "Prohibited shell commands & subprocess injection neutralization"], 
         "orange", 1060, 360),

        ("TIER 2 — INTEGRATION SUBSYSTEM TESTING", "28 TESTS", "Multi-module communication and data contract validation", 
         ["Incident Intake -> Deterministic Normalization pipeline", "Runbook Corpus -> scikit-learn TF-IDF Vectorization pipeline", "Human Approval Gate -> Safe Simulation Executor contract"], 
         "green", 1240, 230),

        ("TIER 1 — UNIT TESTING & MODEL CONSTRAINTS", "52 TESTS", "Core entity logic, mathematical functions, and state machines", 
         ["Entity field constraints, unique identifiers (INC-XXXX, RB-XXXX)", "Deterministic regex keyword triage (Intent, Service, Priority)", "Cosine similarity mathematical calculations and citation extraction", "14 allowlisted Python mock actions in SAFE_ACTIONS"], 
         "blue", 1420, 100)
    ]

    for title, badge, desc, items, thm, w, y in tiers:
        x = (1600 - w) / 2
        draw_card(ax, x, y, w, 110, title, [desc] + items[:2], theme=thm, badge=badge, corner_radius=10, align='left', title_size=9.5, body_size=8)

    # Downward pyramid arrows
    for y_ar in [620, 490, 360, 230]:
        draw_arrow(ax, 800, y_ar, 800, y_ar - 18, color="#64748B", lw=1.5)

    # Bottom Summary Banner
    b_box = patches.FancyBboxPatch((90, 50), 1420, 38, boxstyle="round,pad=0,rounding_size=6",
                                   facecolor="#F0FDF4", edgecolor="#22C55E", linewidth=1.2, zorder=2)
    ax.add_patch(b_box)
    ax.text(800, 69, "AUTOMATED REGRESSION SUITE: 120 / 120 TESTS PASSING (100% PASS RATE) ACROSS PHASES 1–8", 
            fontsize=9.5, fontweight='bold', color="#166534", ha='center', va='center', zorder=3)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "11_Testing_Strategy_Diagram.png"))


# ==============================================================================
# DIAGRAM 12: Security and Privacy Architecture
# ==============================================================================
def generate_diagram_12():
    fig, ax = create_canvas(
        title="Security and Privacy Architecture — Defense-in-Depth",
        subtitle="Multi-Layered Protection: Authentication, RBAC, Safe Allowlisting & Air-Gapped Privacy"
    )

    # Top: Authentication & RBAC Layer
    draw_card(ax, 70, 600, 440, 150, "LAYER 1: AUTHENTICATION & ACCESS CONTROL", [
        "Django Session Authentication (PBKDF2 SHA-256)",
        "Secure HttpOnly Cookie Storage & CSRF Token Validation",
        "Role-Based Access Control (RBAC): Employee vs IT Admin",
        "Persona Decorators: @employee_required, @it_admin_required",
        "Object-Level Access: Users restricted to own tickets"
    ], theme="blue", badge="INGRESS GATE", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 510, 675, 590, 675, color="#2563EB", lw=2)

    # Top Right: Air-Gapped Local Privacy Layer
    draw_card(ax, 590, 600, 460, 150, "LAYER 2: AIR-GAPPED PRIVACY GUARANTEE", [
        "100% Local NLP Execution (scikit-learn TF-IDF)",
        "Zero External AI APIs (No OpenAI, Gemini, or Cloud LLMs)",
        "Zero Data Exfiltration: Ticket data never leaves host memory",
        "Synthetic Data Privacy: No real user PII in demonstration data",
        "Deterministic classification with zero hallucination risk"
    ], theme="green", badge="AIR GAPPED", corner_radius=10, align='left', title_size=10, body_size=8.5)

    draw_arrow(ax, 1050, 675, 1130, 675, color="#16A34A", lw=2)

    # Top Far Right: Security Controls Summary
    draw_card(ax, 1130, 600, 400, 150, "SECURITY CONTROLS MATRIX", [
        "CSRF Protection on all POST requests",
        "100% ORM Parameterized SQL (0 SQLi)",
        "Template HTML Auto-Escaping (0 XSS)",
        "Rate-bounded local vectorization (0 DoS)",
        "Append-Only AuditLog for Non-Repudiation"
    ], theme="purple", badge="STANDARDS", corner_radius=10, align='left', title_size=10, body_size=8.5)

    # Middle Banner: 5-Stage Automation Security Filter Chain
    chain_box = patches.FancyBboxPatch((70, 420), 1460, 145, boxstyle="round,pad=0,rounding_size=12",
                                       facecolor="#FFF7ED", edgecolor="#F97316", linewidth=1.5, zorder=1)
    ax.add_patch(chain_box)
    ax.text(90, 545, "5-STAGE AUTOMATION DEFENSE-IN-DEPTH FILTER CHAIN", fontsize=11, fontweight='bold', color="#7C2D12")

    chain_steps = [
        ("1. Requested Action", "Triggered by recommended SOP", 90),
        ("2. Admin Authorization", "@it_admin_required check", 380),
        ("3. Human Approval Gate", "Explicit status == APPROVED", 670),
        ("4. Allowlist Validation", "Checked in SAFE_ACTIONS", 960),
        ("5. Pure Python Execution", "Zero Subprocess / No Shell", 1250)
    ]
    for ctitle, cdesc, cx in chain_steps:
        draw_card(ax, cx, 435, 260, 85, ctitle, [cdesc], theme="orange" if "Approval" in ctitle else "green", corner_radius=8, align='center', title_size=9, body_size=8)
        if cx < 1250:
            draw_arrow(ax, cx + 260, 477, cx + 290, 477, color="#EA580C", lw=1.8)

    # Bottom: Allowed vs Blocked State Enforcements
    # Left: Allowed States (Green)
    draw_card(ax, 70, 80, 710, 310, "ALLOWED OPERATIONAL PATHWAYS", [
        "Authenticated Employee viewing owned incidents (created_by == request.user)",
        "Authenticated Employee submitting 1 to 5 star rating on resolved ticket",
        "Authenticated IT Admin inspecting full incident queue and authoring SOP runbooks",
        "Authenticated IT Admin requesting approval with 7 verified diagnostic preconditions",
        "Authenticated IT Admin explicitly approving allowlisted simulation remediation",
        "Simulated in-process execution of allowlisted functions (e.g. restart_nginx, check_disk)",
        "Post-execution verification PASSED -> automatic incident transition to RESOLVED"
    ], theme="green", badge="VERIFIED ALLOWED", corner_radius=12, align='left', title_size=11, body_size=8.5)

    # Right: Blocked Threat States (Red)
    draw_card(ax, 820, 80, 710, 310, "STRICTLY BLOCKED & NEUTRALIZED THREATS", [
        "Unauthenticated or Employee access to admin approval endpoints -> HTTP 403 / Redirect",
        "Execution attempt without prior human approval (PENDING) -> BLOCKED + AuditLog",
        "Execution attempt on REJECTED approval -> BLOCKED + AuditLog",
        "Execution attempt on unlisted / dangerous command (e.g. rm_rf, delete_db) -> BLOCKED",
        "Arbitrary operating system command execution (os.system, subprocess) -> CATEGORICALLY ABSENT",
        "Execution attempt on inactive / deprecated runbook -> BLOCKED",
        "Duplicate execution on already successful approval -> BLOCKED by Idempotency Guard"
    ], theme="red", badge="BLOCKED & LOGGED", corner_radius=12, align='left', title_size=11, body_size=8.5)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "12_Security_Privacy_Architecture.png"))


# ==============================================================================
# DIAGRAM 13: Deployment Architecture
# ==============================================================================
def generate_diagram_13():
    fig, ax = create_canvas(
        title="AIOps Service Desk — Deployment Architecture",
        subtitle="Runtime Infrastructure: Browser Ingress, Django Web Tier, In-Process Local NLP & Persistent Storage"
    )

    # 1. Client Browser Tier
    draw_card(ax, 70, 460, 320, 280, "CLIENT TIER: WEB BROWSER", [
        "HTML5 / CSS3 / Bootstrap 5 / JavaScript",
        "Modern Browsers (Chrome, Edge, Firefox, Safari)",
        "HTTPS / HTTP Ingress (Default Port 8000)",
        "Interactive Employee Self-Service Desk",
        "Interactive IT Admin Management Console",
        "Real-Time Diagnostic Checklists & Dry-Run UI",
        "Responsive Grid & Accessibility Compliant"
    ], theme="blue", badge="CLIENT ACCESS", corner_radius=12, align='left', title_size=11, body_size=8.5)

    draw_arrow(ax, 390, 600, 470, 600, label="HTTP :8000", color="#2563EB", lw=2, label_offset=(0, 12))

    # 2. Django Web Application Server Tier
    draw_card(ax, 470, 370, 480, 370, "APPLICATION TIER: DJANGO CORE SERVER", [
        "Python 3.11+ / Django 6.0.7 MVC Engine",
        "URL Dispatcher & View Layer Routing",
        "Django Authentication & RBAC Decorators",
        "App Module: `accounts` (Profiles & Access)",
        "App Module: `incidents` (Triage & Ticketing)",
        "App Module: `runbooks` (SOP Catalog & Citations)",
        "App Module: `automation` (Approvals & Simulation)",
        "Static Assets (CSS, JS, Fonts, Bootstrap Icons)",
        "Server-Side HTML Template Rendering Engine"
    ], theme="dark", badge="WEB BACKEND", corner_radius=14, align='left', title_size=12, body_size=9)

    draw_arrow(ax, 950, 600, 1030, 600, color="#2563EB", lw=2)

    # 3. Local NLP Engine Tier
    draw_card(ax, 1030, 460, 500, 280, "LOCAL NLP RETRIEVAL ENGINE", [
        "scikit-learn 1.6+ TfidfVectorizer Library",
        "In-Process Memory Vector Space Matrix",
        "Linear Dot-Product Cosine Similarity Engine",
        "Configurable Threshold Filter (>= 0.20 Cutoff)",
        "Sub-10ms Vectorization & Matching Latency",
        "Verifiable Citation & Evidence Synthesis",
        "100% Air-Gapped (Zero External Cloud AI APIs)"
    ], theme="green", badge="IN-PROCESS NLP", corner_radius=12, align='left', title_size=11, body_size=8.5)

    # 4. Database Tier (Bottom Left/Center)
    draw_arrow(ax, 710, 370, 710, 250, color="#64748B", lw=2)

    draw_card(ax, 470, 70, 480, 180, "DATA TIER: SQLITE RELATIONAL DATABASE", [
        "Default Storage: `db.sqlite3` file-based database",
        "ACID Compliant Transactional Integrity",
        "Parameterized Django ORM Queries (0 SQL Injection)",
        "Single-File Portability: Zero external server dependencies",
        "Capacity: Easily handles up to 50,000 incident records"
    ], theme="gray", badge="DEFAULT STORAGE", corner_radius=12, align='left', title_size=11, body_size=8.5)

    # 5. Optional Containerized Deployment (Right Bottom)
    draw_card(ax, 1030, 70, 500, 350, "OPTIONAL CONTAINERIZED DEPLOYMENT", [
        "Designated as OPTIONAL deployment architecture",
        "Multi-Stage Dockerfile (python:3.11-slim, non-root user)",
        "docker-compose.yml configuration with volume mounts:",
        "  • ./db.sqlite3:/app/db.sqlite3 (Persistent database)",
        "  • ./static:/app/static (Static web assets)",
        "  • ./data:/app/data (Evaluation test suites)",
        "Healthcheck probe: /login/ endpoint monitoring",
        "Documented Production Roadmap: PostgreSQL 16+ option"
    ], theme="orange", badge="OPTIONAL DOCKER", corner_radius=12, align='left', title_size=11, body_size=8.5)

    draw_arrow(ax, 950, 160, 1030, 160, color="#F97316", lw=1.5, ls="--")

    save_diagram(fig, os.path.join(OUTPUT_DIR, "13_Deployment_Architecture.png"))


# ==============================================================================
# DIAGRAM 14: Future Scope and Enhancement Roadmap
# ==============================================================================
def generate_diagram_14():
    fig, ax = create_canvas(
        title="Future Scope and Enhancement Roadmap",
        subtitle="Strategic Engineering Evolution: From Current Air-Gapped MVP to Enterprise Autonomous Operations"
    )

    # Stage 0: Current MVP Anchor (Leftmost)
    draw_card(ax, 70, 100, 290, 640, "CURRENT MVP\n(Completed & Verified)", [
        "Django 6.0.7 MVC Architecture",
        "SQLite 3 File Database",
        "Local scikit-learn TF-IDF",
        "Linear Cosine Similarity",
        "Deterministic Regex Triage",
        "Explainable Citation Evidence",
        "7-Point Diagnostic Checklist",
        "Read-Only Dry-Run Mode",
        "Human Approval Gate",
        "14 Allowlisted Mock Actions",
        "Simulation Mode Execution",
        "Post-Execution Verification",
        "1 to 5 Star Feedback Loop",
        "Append-Only AuditLog",
        "120 Automated Tests (100%)"
    ], theme="green", badge="CURRENT BASELINE", corner_radius=14, align='left', title_size=11, body_size=8.5)

    # Arrow to Future Stages
    draw_arrow(ax, 360, 420, 430, 420, label="ROADMAP", color="#2563EB", lw=2.5, label_offset=(0, 14), label_color="#1D4ED8")

    # Future Stages 1 to 6 (Grid of 2 rows x 3 columns on right)
    future_stages = [
        ("STAGE 1: DATABASE EVOLUTION", "High-Scale Relational Backend", [
            "Migrate from SQLite to PostgreSQL 16+",
            "pgvector extension for high-dimensional vector search",
            "Connection pooling with PgBouncer for high concurrency"
        ], "blue", 430, 440),

        ("STAGE 2: EMBEDDING RETRIEVAL", "Dense Semantic Vector Models", [
            "Local sentence-transformers (all-MiniLM-L6-v2)",
            "Captures deep contextual synonyms beyond TF-IDF",
            "Multi-lingual ticket query matching and normalization"
        ], "blue", 800, 440),

        ("STAGE 3: REAL AUTOMATION SANDBOX", "Safe Real-World Execution", [
            "Isolated Docker container execution workers",
            "Ansible / SaltStack / Terraform playbook integration",
            "Automated rollback scripts for reversible actions"
        ], "orange", 1170, 440),

        ("STAGE 4: ENTERPRISE TELEMETRY", "Full-Stack Observability", [
            "OpenTelemetry distributed tracing spans across workflow",
            "Prometheus metrics exporter for MTTR and SLA tracking",
            "Grafana live dashboards for operations analytics"
        ], "orange", 430, 160),

        ("STAGE 5: DISTRIBUTED SCALE", "High-Availability Deployment", [
            "Kubernetes (K8s) deployment manifests & Helm charts",
            "Celery task workers + Redis message broker queues",
            "Enterprise SSO integration (SAML 2.0, OAuth2, LDAP)"
        ], "purple", 800, 160),

        ("STAGE 6: KNOWLEDGE COPILOT", "Continuous Procedure Evolution", [
            "Automated runbook drafting from resolved high-rated tickets",
            "Reinforcement Learning from Human Feedback (RLHF)",
            "Automated drift detection on operational procedures"
        ], "purple", 1170, 160)
    ]

    for title, sub, bullets, thm, fx, fy in future_stages:
        draw_card(ax, fx, fy, 350, 250, title, [f"Goal: {sub}", ""] + bullets, 
                  theme=thm, badge="FUTURE SCOPE", corner_radius=12, align='left', title_size=10, body_size=8.5)

    # Connecting arrows across future stages
    draw_arrow(ax, 780, 565, 800, 565, color="#94A3B8", lw=1.5)
    draw_arrow(ax, 1150, 565, 1170, 565, color="#94A3B8", lw=1.5)
    draw_arrow(ax, 1345, 440, 1345, 410, color="#94A3B8", lw=1.5, style="-")
    draw_arrow(ax, 1345, 410, 605, 410, color="#94A3B8", lw=1.5, style="-")
    draw_arrow(ax, 605, 410, 605, 410, color="#94A3B8", lw=1.5, style="-|>")
    draw_arrow(ax, 780, 285, 800, 285, color="#94A3B8", lw=1.5)
    draw_arrow(ax, 1150, 285, 1170, 285, color="#94A3B8", lw=1.5)

    # Bottom Scope Delineation Banner
    f_box = patches.FancyBboxPatch((430, 80), 1090, 50, boxstyle="round,pad=0,rounding_size=8",
                                   facecolor="#FEF2F2", edgecolor="#EF4444", linewidth=1.2, zorder=2)
    ax.add_patch(f_box)
    ax.text(975, 105, "DELINEATION NOTICE: STAGES 1 THROUGH 6 ARE STRICTLY DESIGNATED AS FUTURE SCOPE FOR CAPSTONE REPORT", 
            fontsize=9.5, fontweight='bold', color="#991B1B", ha='center', va='center', zorder=3)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "14_Future_Scope_Roadmap.png"))


if __name__ == "__main__":
    print("Generating Diagrams 08 to 14...")
    generate_diagram_08()
    generate_diagram_09()
    generate_diagram_10()
    generate_diagram_11()
    generate_diagram_12()
    generate_diagram_13()
    generate_diagram_14()
    print("Diagrams 08 to 14 successfully generated!")
