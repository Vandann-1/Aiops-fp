"""
Generates Technical Diagrams 01 to 07 for the AIOps Service Desk Capstone Report.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from diagram_utils import create_canvas, draw_card, draw_arrow, save_diagram, THEMES, BG_WHITE, TEXT_NAVY, TEXT_MUTED

OUTPUT_DIR = "Project Report/Diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# DIAGRAM 01: Current vs Proposed IT Support Process
# ==============================================================================
def generate_diagram_01():
    fig, ax = create_canvas(
        title="Current vs Proposed IT Support Process",
        subtitle="Comparative Operational Analysis: Fragmented Manual Triage vs Bounded AIOps Assistance"
    )

    # Left Container: Current Process
    box_curr = patches.FancyBboxPatch((70, 75), 650, 680, boxstyle="round,pad=0,rounding_size=14",
                                     facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5, zorder=1)
    ax.add_patch(box_curr)
    ax.text(395, 725, "CURRENT IT SUPPORT PROCESS", fontsize=13, fontweight='bold', color="#991B1B", ha='center', va='center')
    ax.text(395, 705, "(Manual, Disconnected & High Latency)", fontsize=9.5, color=TEXT_MUTED, ha='center', va='center')

    curr_steps = [
        "User Reports Issue",
        "Support Reads Ticket",
        "Manual Runbook Search",
        "Manual Diagnosis",
        "Manual Decision",
        "Manual Remediation",
        "Resolution"
    ]
    curr_y = 650
    for i, step in enumerate(curr_steps):
        draw_card(ax, 110, curr_y - 38, 260, 42, step, theme="gray", corner_radius=8, title_size=9.5)
        if i < len(curr_steps) - 1:
            draw_arrow(ax, 240, curr_y - 38, 240, curr_y - 65, color="#94A3B8")
            curr_y -= 65

    # Current Pain Points (Red Callouts on Right of Left Container)
    pain_points = [
        ("Scattered Knowledge", "Unindexed Wiki docs & static PDFs", 570),
        ("Manual Diagnosis", "Subjective error interpretation", 480),
        ("Time-Consuming Process", "Hours lost in queues & back-and-forth", 390),
        ("Experience Dependency", "Siloed expertise across senior staff", 300),
        ("Risk of Human Error", "Accidental commands & missed steps", 210)
    ]
    for title, desc, py in pain_points:
        draw_card(ax, 400, py - 32, 290, 46, title, [desc], theme="red", corner_radius=8, align='left', title_size=9, body_size=8)
        draw_arrow(ax, 370, py - 9, 395, py - 9, color="#EF4444", lw=1.2)

    # Center Bridge Transition
    ax.text(800, 440, "PARADIGM\nSHIFT", fontsize=11, fontweight='bold', color="#2563EB", ha='center', va='center')
    draw_arrow(ax, 730, 415, 870, 415, label="Bounded AIOps", color="#2563EB", lw=2.5, label_offset=(0, 18), label_color="#1D4ED8")

    # Right Container: Proposed Process
    box_prop = patches.FancyBboxPatch((880, 75), 650, 680, boxstyle="round,pad=0,rounding_size=14",
                                     facecolor="#F0FDF4", edgecolor="#86EFAC", linewidth=1.5, zorder=1)
    ax.add_patch(box_prop)
    ax.text(1205, 725, "PROPOSED AIOps SERVICE DESK", fontsize=13, fontweight='bold', color="#166534", ha='center', va='center')
    ax.text(1205, 705, "(Deterministic Triage, Explainable NLP & Human Approval)", fontsize=9.5, color=TEXT_MUTED, ha='center', va='center')

    # Two columns of streamlined steps on right
    prop_col1 = [
        ("01 Incident Ingestion", "Structured forms & API intake", "blue"),
        ("02 Classification", "Deterministic Intent & Service", "blue"),
        ("03 Runbook Retrieval", "Local TF-IDF & Cosine Match", "blue"),
        ("04 Citation / Evidence", "Matched symptoms & cited steps", "blue"),
        ("05 Diagnostic Checklist", "7 live pre-execution state checks", "orange")
    ]
    prop_col2 = [
        ("06 Human Approval", "Mandatory Admin Review Gate", "orange"),
        ("07 Safe Automation", "Allowlisted simulation execution", "green"),
        ("08 Verification", "Simulated health check gate", "green"),
        ("09 Resolution", "Automatic transition to Resolved", "green"),
        ("10 Audit + Feedback", "1-5★ telemetry & knowledge update", "purple")
    ]

    p_y = 650
    for title, desc, thm in prop_col1:
        draw_card(ax, 905, p_y - 42, 285, 48, title, [desc], theme=thm, corner_radius=8, align='left', title_size=9, body_size=8)
        p_y -= 68

    # Arrow from col 1 bottom to col 2 top
    draw_arrow(ax, 1047, 335, 1262, 608, color="#16A34A", lw=1.8, style="-|>")

    p_y2 = 650
    for title, desc, thm in prop_col2:
        draw_card(ax, 1220, p_y2 - 42, 285, 48, title, [desc], theme=thm, corner_radius=8, align='left', title_size=9, body_size=8)
        p_y2 -= 68

    # Col 1 arrows
    for y_ar in [582, 514, 446, 378]:
        draw_arrow(ax, 1047, y_ar, 1047, y_ar - 26, color="#3B82F6")

    # Col 2 arrows
    for y_ar in [582, 514, 446, 378]:
        draw_arrow(ax, 1362, y_ar, 1362, y_ar - 26, color="#22C55E")

    save_diagram(fig, os.path.join(OUTPUT_DIR, "01_Current_vs_Proposed_IT_Support_Process.png"))


# ==============================================================================
# DIAGRAM 02: Stakeholder & Persona Diagram
# ==============================================================================
def generate_diagram_02():
    fig, ax = create_canvas(
        title="Stakeholder & System Persona Architecture",
        subtitle="Role-Based Responsibilities and Human-in-the-Loop Operational Boundaries"
    )

    # Center Hub: AIOps Service Desk
    draw_card(ax, 610, 270, 380, 260, "AIOps SERVICE DESK", 
              [
                  "Central System Orchestrator",
                  "Role-Based Access Control (RBAC)",
                  "Finite State Machine Lifecycle",
                  "Append-Only AuditLog Engine",
                  "Air-Gapped Local Architecture"
              ], 
              theme="dark", corner_radius=16, title_size=13, body_size=9.5)

    # Left: Employee Persona
    draw_card(ax, 80, 270, 430, 260, "EMPLOYEE PERSONA", 
              [
                  "Submit new incident tickets with category & severity",
                  "Inspect personal ticket queue (ownership filtered)",
                  "View explainable AI runbook recommendation & citations",
                  "Track real-time resolution timeline & status",
                  "Submit 1 to 5 star rating & feedback upon resolution"
              ], 
              theme="blue", badge="SERVICE CONSUMER", corner_radius=14, align='left', title_size=12, body_size=9)

    # Right: IT Admin Persona
    draw_card(ax, 1090, 270, 430, 260, "IT ADMIN PERSONA", 
              [
                  "Triage & manage complete organization incident queue",
                  "Author, maintain, and activate/deactivate runbooks",
                  "Review AI recommendations & inspect 7-point checklist",
                  "Explicitly approve or reject automation requests",
                  "Trigger controlled mock execution & run verification",
                  "Review audit logs, telemetry, and knowledge feedback"
              ], 
              theme="orange", badge="OPERATOR & REVIEWER", corner_radius=14, align='left', title_size=12, body_size=9)

    # Bottom: AIOps System Persona
    draw_card(ax, 470, 75, 660, 145, "AIOps AUTOMATED CORE ENGINE", 
              [
                  "Deterministic Ticket Normalization (Intent, Service, Priority classification)",
                  "Local scikit-learn TF-IDF Vectorization & Cosine Similarity Runbook Retrieval",
                  "Verifiable Citation & Evidence Extraction (Matched symptoms, cited action steps)",
                  "Pre-Execution Diagnostic State Verification & Safe Allowlist Enforcement (SAFE_ACTIONS)",
                  "Automated Chronological Event Auditing (AuditLog & IncidentActivity)"
              ], 
              theme="green", badge="AUTONOMOUS ASSISTANT", corner_radius=14, align='left', title_size=11, body_size=8.5)

    # Connectors & Human-in-the-Loop Gate
    # Employee <-> Center
    draw_arrow(ax, 510, 420, 610, 420, label="Report Incidents", color="#2563EB", lw=1.8, label_offset=(0, 12))
    draw_arrow(ax, 610, 370, 510, 370, label="Recommendations & Status", color="#64748B", lw=1.5, label_offset=(0, -12))

    # IT Admin <-> Center
    draw_arrow(ax, 1090, 420, 990, 420, label="Review & Decision", color="#EA580C", lw=2, label_offset=(0, 12), label_color="#C2410C")
    draw_arrow(ax, 990, 370, 1090, 370, label="Triage & Checklists", color="#64748B", lw=1.5, label_offset=(0, -12))

    # Center <-> AIOps System
    draw_arrow(ax, 750, 270, 750, 220, label="Trigger Retrieval", color="#16A34A", lw=1.8, label_offset=(-45, 0))
    draw_arrow(ax, 850, 220, 850, 270, label="Match Scores & Citations", color="#16A34A", lw=1.8, label_offset=(55, 0))

    # Human-in-the-Loop Banner
    hil_box = patches.FancyBboxPatch((600, 580), 400, 46, boxstyle="round,pad=0,rounding_size=8",
                                     facecolor="#FFF7ED", edgecolor="#F97316", linewidth=1.5, zorder=3)
    ax.add_patch(hil_box)
    ax.text(800, 603, "HUMAN-IN-THE-LOOP CONTROL GATE", fontsize=10.5, fontweight='bold', color="#C2410C", ha='center', va='center', zorder=4)

    draw_arrow(ax, 1150, 530, 890, 580, color="#F97316", lw=1.8, ls="--")
    draw_arrow(ax, 800, 580, 800, 530, color="#F97316", lw=1.8, style="-|>")

    save_diagram(fig, os.path.join(OUTPUT_DIR, "02_Stakeholder_Persona_Diagram.png"))


# ==============================================================================
# DIAGRAM 03: Misuse and Abuse Cases
# ==============================================================================
def generate_diagram_03():
    fig, ax = create_canvas(
        title="Misuse and Abuse Cases — System Threat Boundaries",
        subtitle="Security Constraints: Systematic Enforcement Gates Neutralizing Prohibited Actions"
    )

    # Central Legitimate Workflow (Horizontal Flow)
    center_y = 440
    legit_steps = [
        ("Incident Ingestion", 70),
        ("AI Recommendation", 280),
        ("Human Approval", 490),
        ("Safety Validation", 700),
        ("Controlled Mock Exec", 910),
        ("Post-Verification", 1120),
        ("Resolution", 1330)
    ]
    for name, x in legit_steps:
        thm = "orange" if "Approval" in name else ("green" if "Resolution" in name or "Exec" in name else "blue")
        draw_card(ax, x, center_y - 28, 170, 56, name, theme=thm, corner_radius=8, title_size=9.5)
        if x < 1330:
            draw_arrow(ax, x + 170, center_y, x + 210, center_y, color="#2563EB", lw=1.8)

    # 7 Abuse / Threat Scenarios
    threats = [
        # (Title, Attack Vector, Target Step X, Target Step Y, Is Top)
        ("1. Unauthorized Employee Action", "Employee posts to admin approval endpoints", 490, 580, True, "Role Check (@it_admin_required)"),
        ("2. Direct Unauthenticated Request", "Direct execution request bypassing login/CSRF", 910, 580, True, "CSRF + Auth Middleware"),
        ("3. Unapproved Action Execution", "Attempting execution while approval is PENDING", 700, 680, True, "State Machine Check (status == APPROVED)"),
        ("4. Unknown Action / Shell Injection", "Injecting 'rm -rf' or arbitrary shell commands", 910, 260, False, "Allowlist Check (SAFE_ACTIONS)"),
        ("5. Inactive Runbook Execution", "Triggering archived or deprecated runbook", 700, 160, False, "Runbook Status Check (is_active == True)"),
        ("6. Duplicate Successful Execution", "Triggering second run on completed action", 1120, 260, False, "Idempotency Guard (status == SUCCESS)"),
        ("7. Execution Failure / Non-Recovery", "Mock action failure or negative verification", 1330, 260, False, "Verification Gate (Remains OPEN)")
    ]

    for title, desc, tx, ty, is_top, gate in threats:
        # Threat Box (Red)
        draw_card(ax, tx - 70, ty, 310, 52, title, [desc], theme="red", corner_radius=8, align='left', title_size=8.5, body_size=7.5)
        
        # Defense Gate Pill
        gate_y = (ty - 22) if is_top else (ty + 60)
        draw_card(ax, tx - 40, gate_y, 250, 24, gate, theme="dark", corner_radius=6, title_size=7.5)

        # Connection to workflow
        dest_y = center_y + 28 if is_top else center_y - 28
        draw_arrow(ax, tx + 85, ty if not is_top else ty - 2, tx + 85, dest_y, label="BLOCKED", 
                   color="#EF4444", lw=1.6, label_color="#DC2626", label_bg="#FEE2E2", label_size=7.5)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "03_Misuse_Abuse_Case_Diagram.png"))


# ==============================================================================
# DIAGRAM 04: Functional Module Diagram
# ==============================================================================
def generate_diagram_04():
    fig, ax = create_canvas(
        title="Functional Modules of the AIOps Service Desk",
        subtitle="Decomposition of Core Subsystems and Inter-Module Collaboration Contracts"
    )

    # 5 Major Functional Blocks
    # 1. User Management (Top Left)
    draw_card(ax, 70, 480, 430, 260, "USER MANAGEMENT SUBSYSTEM (`accounts`)", [
        "Django Session Authentication (PBKDF2 SHA-256)",
        "Role-Based Access Control (RBAC)",
        "Persona Decorators (@employee_required, @it_admin_required)",
        "User Profiles & Departmental Attribution",
        "Object-Level Incident Ownership Enforcement"
    ], theme="blue", corner_radius=12, align='left', title_size=10.5, body_size=8.5)

    # 2. Knowledge Subsystem (Top Right)
    draw_card(ax, 550, 480, 460, 260, "KNOWLEDGE BASE SUBSYSTEM (`runbooks`)", [
        "Canonical Standard Operating Procedures (SOP)",
        "Indicative Symptoms & Keyword Corpus Indexing",
        "Air-Gapped Local scikit-learn TfidfVectorizer",
        "Linear Cosine Similarity Computation Engine",
        "Threshold Filtering (Min Score >= 0.20 Cutoff)",
        "Explainable Citation & Evidence Extraction"
    ], theme="green", corner_radius=12, align='left', title_size=10.5, body_size=8.5)

    # 3. Governance Subsystem (Top Far Right)
    draw_card(ax, 1060, 480, 470, 260, "GOVERNANCE & TELEMETRY SUBSYSTEM", [
        "Chronological Append-Only AuditLog Engine",
        "IncidentActivity Timeline Event Stream",
        "Continuous 1 to 5 Star Post-Resolution Feedback Loop",
        "Standard Structured Python Logging (10 Core Events)",
        "Capstone Overview Console & Live DB Metrics"
    ], theme="purple", corner_radius=12, align='left', title_size=10.5, body_size=8.5)

    # 4. Service Desk Subsystem (Bottom Left)
    draw_card(ax, 70, 100, 680, 330, "SERVICE DESK CORE SUBSYSTEM (`incidents`)", [
        "Sequential Incident Ingestion (INC-XXXX numbering format)",
        "Deterministic Regex & Keyword Ticket Normalization Engine",
        "Algorithmic Intent Triage (Outage, Degradation, Access, DB, Network, Storage)",
        "Algorithmic Service Mapping (Web Server, Database, Network, Storage, Auth)",
        "Suggested Priority Assignment (P1, P2, P3, P4 SLAs)",
        "7-Point Pre-Execution Diagnostic State Checklist Evaluator",
        "Interactive Employee Feedback Capture Interface"
    ], theme="blue", corner_radius=12, align='left', title_size=11, body_size=8.5)

    # 5. Automation Control Subsystem (Bottom Right)
    draw_card(ax, 800, 100, 730, 330, "AUTOMATION CONTROL & SAFETY SUBSYSTEM (`automation`)", [
        "Human-in-the-Loop Review Panel & Decision State Machine",
        "Read-Only Dry-Run Simulation Preview Engine",
        "Predefined Safe Action Registry (14 Allowlisted Python Mocks)",
        "Reversibility & Rollback Guidance Metadata Catalog",
        "Strict In-Process Executor (Zero Shell / Subprocess Execution Guarantee)",
        "Post-Execution Health Verification Check Gate",
        "Automated Incident State Transition to RESOLVED"
    ], theme="orange", corner_radius=12, align='left', title_size=11, body_size=8.5)

    # Inter-Module Dataflow Arrows
    draw_arrow(ax, 410, 430, 600, 480, label="Incident Text", color="#2563EB", lw=1.5)
    draw_arrow(ax, 780, 480, 950, 430, label="Recommended Runbook + Citation", color="#16A34A", lw=1.5)
    draw_arrow(ax, 750, 260, 800, 260, label="Ticket Context", color="#3B82F6", lw=1.8)
    draw_arrow(ax, 1165, 430, 1165, 480, label="Audit Events & Feedback", color="#A855F7", lw=1.5)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "04_Functional_Module_Diagram.png"))


# ==============================================================================
# DIAGRAM 05: Main Solution Architecture
# ==============================================================================
def generate_diagram_05():
    fig, ax = create_canvas(
        title="Solution Architecture — AIOps Service Desk",
        subtitle="5-Tier Layered Architecture: Clean Separation of Concerns with Air-Gapped Local NLP"
    )

    layers = [
        # (Title, Theme, Sub-components list, Y, Height)
        ("LAYER 1 — USERS & PERSONAS", "blue", [
            ("Employee Persona", "Ticket Creation & Feedback"),
            ("IT Admin Persona", "Triage, Approvals, Execution, KB Management")
        ], 660, 95),
        ("LAYER 2 — PRESENTATION & WEB APPLICATION TIER", "dark", [
            ("Django 6.0.7 MVC Framework", "URL Routing, Views, Middleware"),
            ("Bootstrap 5 & Vanilla JS", "Responsive Admin & Employee Portals"),
            ("CSRF Protection & RBAC Decorators", "Security Enforcement Layer")
        ], 515, 115),
        ("LAYER 3 — APPLICATION BUSINESS LOGIC & SAFETY GATES", "orange", [
            ("Ticket Normalization Engine", "Deterministic Triage"),
            ("Diagnostic Checklist Service", "7 Live State Preconditions"),
            ("Human Approval State Machine", "Pending / Approved / Rejected"),
            ("Safe Simulation Executor", "14 Allowlisted Python Actions"),
            ("Verification Engine", "Post-Execution Health Check Gate")
        ], 340, 145),
        ("LAYER 4 — LOCAL NLP & KNOWLEDGE RETRIEVAL (Zero External AI APIs)", "green", [
            ("Runbook Corpus", "Active SOP Documents"),
            ("scikit-learn TfidfVectorizer", "Local Term Weighting"),
            ("Cosine Similarity Engine", "Linear Dot Product Matching"),
            ("Citation & Evidence Extractor", "Symptoms & Steps Traceability")
        ], 195, 115),
        ("LAYER 5 — PERSISTENT DATA TIER", "gray", [
            ("SQLite Relational Database (Default)", "Self-Contained Portable Storage"),
            ("PostgreSQL + pgvector (Documented)", "Enterprise Scale Production Path"),
            ("Append-Only AuditLog Table", "Immutable Regulatory Compliance Log")
        ], 65, 100)
    ]

    for title, thm, comps, ly, lh in layers:
        # Layer Background Band
        band = patches.FancyBboxPatch((70, ly), 1460, lh, boxstyle="round,pad=0,rounding_size=10",
                                      facecolor=THEMES[thm]["fill"], edgecolor=THEMES[thm]["border"], linewidth=1.4, zorder=1)
        ax.add_patch(band)
        ax.text(90, ly + lh - 18, title, fontsize=9.5, fontweight='bold', color=THEMES[thm]["text"], family='sans-serif', zorder=2)

        # Child Component Cards within Layer
        spacing = 1420 / len(comps)
        for idx, (cname, cdesc) in enumerate(comps):
            cx = 90 + idx * spacing
            cw = spacing - 20
            draw_card(ax, cx, ly + 10, cw, lh - 36, cname, [cdesc], theme=thm, corner_radius=6, align='center', title_size=8.5, body_size=7.5)

    # Vertical downward connectivity arrows between layers
    draw_arrow(ax, 800, 660, 800, 630, color="#64748B", lw=1.5)
    draw_arrow(ax, 800, 515, 800, 485, color="#64748B", lw=1.5)
    draw_arrow(ax, 800, 340, 800, 310, color="#64748B", lw=1.5)
    draw_arrow(ax, 800, 195, 800, 165, color="#64748B", lw=1.5)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "05_Main_Solution_Architecture.png"))


# ==============================================================================
# DIAGRAM 06: End-to-End Workflow
# ==============================================================================
def generate_diagram_06():
    fig, ax = create_canvas(
        title="End-to-End AIOps Incident Resolution Workflow",
        subtitle="Lifecycle State Progression: Deterministic Triage, Human Gate, Safe Automation & Verification"
    )

    # Stage 1: Intake & Triage (Top Row, Left to Right)
    steps_row1 = [
        ("01 Incident Created", "User submits raw symptom report", 70),
        ("02 Normalization", "Remove conversational noise", 260),
        ("03 Triage Logic", "Intent, Service, Priority extracted", 450),
        ("04 Local NLP Match", "TF-IDF + Cosine Similarity", 640),
        ("05 Citation Gen", "Extract matched symptoms & steps", 830),
        ("06 Safety Checklist", "Evaluate 7 live preconditions", 1020),
        ("07 Approval Request", "Status: PENDING_APPROVAL", 1210),
        ("08 Human Review", "Admin inspects dry-run preview", 1400)
    ]
    for title, desc, sx in steps_row1:
        thm = "orange" if "Approval" in title or "Review" in title else "blue"
        draw_card(ax, sx, 660, 140, 65, title, [desc], theme=thm, corner_radius=8, align='center', title_size=8, body_size=7)
        if sx < 1400:
            draw_arrow(ax, sx + 140, 692, sx + 190, 692, color="#3B82F6", lw=1.4)

    # Branching Arrow down from Human Review
    draw_arrow(ax, 1470, 660, 1470, 560, color="#EA580C", lw=2)

    # Decision 1: Human Approval Gate
    dec1 = patches.RegularPolygon((1470, 510), numVertices=4, radius=45, orientation=0,
                                   facecolor="#FFF7ED", edgecolor="#F97316", linewidth=1.6, zorder=2)
    ax.add_patch(dec1)
    ax.text(1470, 510, "HUMAN\nDECISION", fontsize=8, fontweight='bold', color="#C2410C", ha='center', va='center', zorder=3)

    # Reject Path (Right to Bottom)
    draw_arrow(ax, 1515, 510, 1540, 510, color="#DC2626", lw=1.6)
    draw_card(ax, 1370, 390, 170, 55, "REJECTED ACTION", ["Reason recorded in AuditLog", "Ticket remains in manual queue"], 
              theme="red", corner_radius=8, align='center', title_size=8, body_size=7)
    draw_arrow(ax, 1470, 465, 1470, 445, label="REJECT", color="#DC2626", lw=1.6, label_color="#DC2626")

    # Approve Path (Left to Execution Row)
    draw_arrow(ax, 1425, 510, 1260, 510, label="APPROVE", color="#16A34A", lw=2, label_color="#166534")

    steps_row2 = [
        ("Allowlist Check", "Verify in SAFE_ACTIONS", 1120),
        ("Controlled Mock Exec", "In-process Python execution", 910),
        ("Execution Output", "Status: SUCCESS recorded", 700)
    ]
    for title, desc, sx in steps_row2:
        draw_card(ax, sx, 480, 150, 60, title, [desc], theme="green", corner_radius=8, align='center', title_size=8.5, body_size=7.5)
    draw_arrow(ax, 1120, 510, 1060, 510, color="#16A34A", lw=1.6)
    draw_arrow(ax, 910, 510, 850, 510, color="#16A34A", lw=1.6)

    # Down from Execution Output to Verification Decision
    draw_arrow(ax, 775, 480, 775, 380, color="#16A34A", lw=1.8)

    # Decision 2: Verification Gate
    dec2 = patches.RegularPolygon((775, 330), numVertices=4, radius=45, orientation=0,
                                   facecolor="#EFF6FF", edgecolor="#2563EB", linewidth=1.6, zorder=2)
    ax.add_patch(dec2)
    ax.text(775, 330, "VERIFY\nHEALTH", fontsize=8, fontweight='bold', color="#1D4ED8", ha='center', va='center', zorder=3)

    # Verification Failed Path
    draw_card(ax, 910, 305, 180, 55, "VERIFICATION FAILED", ["Ticket remains OPEN", "Audit recorded, manual takeover"], 
              theme="red", corner_radius=8, align='center', title_size=8, body_size=7)
    draw_arrow(ax, 820, 330, 910, 330, label="FAILED", color="#DC2626", lw=1.6, label_color="#DC2626")

    # Verification Passed Path
    draw_arrow(ax, 730, 330, 600, 330, label="PASSED", color="#16A34A", lw=2, label_color="#166534")

    # Final Resolution Steps (Row 3, Right to Left)
    steps_row3 = [
        ("Auto-Resolution", "Status -> RESOLVED", 420),
        ("AuditLog Recorded", "Append-only compliance trail", 240),
        ("Employee Feedback", "1 to 5 star rating captured", 60)
    ]
    for title, desc, sx in steps_row3:
        draw_card(ax, sx, 300, 140, 60, title, [desc], theme="green" if "Auto" in title else "purple", corner_radius=8, align='center', title_size=8.5, body_size=7.5)
    draw_arrow(ax, 420, 330, 380, 330, color="#16A34A", lw=1.6)
    draw_arrow(ax, 240, 330, 200, 330, color="#A855F7", lw=1.6)

    # Callout Highlight
    callout = patches.FancyBboxPatch((300, 100), 1000, 70, boxstyle="round,pad=0,rounding_size=10",
                                     facecolor="#F8FAFC", edgecolor="#3B82F6", linewidth=1.2, zorder=2)
    ax.add_patch(callout)
    ax.text(800, 148, "CORE SAFETY GUARANTEE: EXECUTION SUCCESS ≠ INCIDENT RESOLUTION", 
            fontsize=11, fontweight='bold', color="#1E3A8A", ha='center', va='center', zorder=3)
    ax.text(800, 122, "Automated resolution is strictly conditional on post-execution verification passing. Zero arbitrary shell commands are permitted.", 
            fontsize=9, color=TEXT_MUTED, ha='center', va='center', zorder=3)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "06_End_to_End_Workflow.png"))


# ==============================================================================
# DIAGRAM 07: Phase 1 to 8 System Development Mapping
# ==============================================================================
def generate_diagram_07():
    fig, ax = create_canvas(
        title="Phase 1–8 System Development Roadmap Mapping",
        subtitle="Evolutionary Engineering Lifecycle: From Baseline Authentication to Governed AIOps Automation"
    )

    phases = [
        ("PHASE 1", "Authentication & Roles", "Secure Role-Based Access Control", "Employee & IT Admin persona boundaries with custom view decorators", "blue"),
        ("PHASE 2", "Incident Management", "Incident Lifecycle Management", "Sequential INC ticketing, status progression, and timeline activity history", "blue"),
        ("PHASE 3", "Knowledge Base", "Centralized SOP Knowledge", "Structured runbooks with indicative symptoms, risk tiers, and automation bindings", "blue"),
        ("PHASE 4", "AI Runbook Retrieval", "Local AI-Assisted Matching", "scikit-learn TF-IDF & Cosine Similarity with explainable citation metadata", "green"),
        ("PHASE 5", "Approval Workflow", "Human Control Before Automation", "Mandatory human review gate with pre-execution 7-point state checklists", "orange"),
        ("PHASE 6", "Safe Automation", "Allowlisted Controlled Execution", "Strict SAFE_ACTIONS registry with pure in-process Python simulation mocks", "orange"),
        ("PHASE 7", "Execution & Verification", "Verify Execution Outcome", "Post-action health checks determining automated resolution or manual takeover", "green"),
        ("PHASE 8", "Audit & Monitoring", "Traceability & Governance", "Append-only AuditLog, structured logging, 1-5★ feedback, and capstone console", "purple")
    ]

    # Grid of 2 rows x 4 columns
    col_w = 330
    row_h = 220
    x_coords = [80, 450, 820, 1190]
    y_coords = [490, 200]

    for idx, (p_num, p_title, p_sub, p_desc, thm) in enumerate(phases):
        col_idx = idx % 4
        row_idx = idx // 4
        px = x_coords[col_idx]
        py = y_coords[row_idx]

        draw_card(ax, px, py, col_w, row_h, f"{p_num}: {p_title}", [
            f"Focus: {p_sub}",
            "",
            p_desc
        ], theme=thm, badge=f"MILESTONE {idx+1}", corner_radius=12, align='left', title_size=10, body_size=8.5)

        # Forward flow arrows
        if col_idx < 3:
            draw_arrow(ax, px + col_w, py + row_h / 2, x_coords[col_idx + 1], py + row_h / 2, color="#94A3B8", lw=1.6)

    # Serpentine arrow from row 1 end to row 2 start
    draw_arrow(ax, 1355, 490, 1355, 455, color="#2563EB", lw=1.8, style="-")
    draw_arrow(ax, 1355, 455, 245, 455, color="#2563EB", lw=1.8, style="-")
    draw_arrow(ax, 245, 455, 245, 420, color="#2563EB", lw=1.8, style="-|>")

    # Bottom Progression Banner
    prog_box = patches.FancyBboxPatch((80, 80), 1440, 55, boxstyle="round,pad=0,rounding_size=10",
                                      facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2, zorder=2)
    ax.add_patch(prog_box)
    ax.text(120, 107, "PROGRESSION DIRECTION:", fontsize=9.5, fontweight='bold', color="#334155", va='center')
    draw_arrow(ax, 310, 107, 1470, 107, label="INCIDENT INTAKE  ───────────────────────────────▶  GOVERNED RESOLUTION", 
               color="#2563EB", lw=2, label_color="#1D4ED8", label_size=10)

    save_diagram(fig, os.path.join(OUTPUT_DIR, "07_Phase_1_to_8_Mapping.png"))


if __name__ == "__main__":
    print("Generating Diagrams 01 to 07...")
    generate_diagram_01()
    generate_diagram_02()
    generate_diagram_03()
    generate_diagram_04()
    generate_diagram_05()
    generate_diagram_06()
    generate_diagram_07()
    print("Diagrams 01 to 07 successfully generated!")
