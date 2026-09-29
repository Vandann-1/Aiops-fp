"""
Diagram Drawing Utilities for AIOps Service Desk Technical Report.
Provides unified styles, color palettes, card renderers, and arrow connectors.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Color Palette
BG_WHITE = "#FFFFFF"
TEXT_NAVY = "#0F172A"       # Primary text
TEXT_MUTED = "#64748B"      # Subtitles / Secondary text
BORDER_DEFAULT = "#CBD5E1"  # Subtle border

# Component Theme Dictionaries
THEMES = {
    "blue": {
        "fill": "#EFF6FF",
        "border": "#3B82F6",
        "text": "#1E3A8A",
        "badge_bg": "#DBEAFE",
        "badge_text": "#1D4ED8"
    },
    "green": {
        "fill": "#F0FDF4",
        "border": "#22C55E",
        "text": "#14532D",
        "badge_bg": "#DCFCE7",
        "badge_text": "#15803D"
    },
    "orange": {
        "fill": "#FFF7ED",
        "border": "#F97316",
        "text": "#7C2D12",
        "badge_bg": "#FFEDD5",
        "badge_text": "#C2410C"
    },
    "red": {
        "fill": "#FEF2F2",
        "border": "#EF4444",
        "text": "#7F1D1D",
        "badge_bg": "#FEE2E2",
        "badge_text": "#B91C1C"
    },
    "gray": {
        "fill": "#F8FAFC",
        "border": "#94A3B8",
        "text": "#334155",
        "badge_bg": "#E2E8F0",
        "badge_text": "#475569"
    },
    "purple": {
        "fill": "#FAF5FF",
        "border": "#A855F7",
        "text": "#581C87",
        "badge_bg": "#F3E8FF",
        "badge_text": "#7E22CE"
    },
    "dark": {
        "fill": "#1E293B",
        "border": "#0F172A",
        "text": "#FFFFFF",
        "badge_bg": "#334155",
        "badge_text": "#E2E8F0"
    }
}

def create_canvas(title, subtitle, tag="AIOPS SERVICE DESK — CAPSTONE TECHNICAL REPORT"):
    """
    Creates a standardized 16:9 canvas with a top header and bottom footer banner.
    Coordinate space: X in [0, 1600], Y in [0, 900].
    """
    fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor(BG_WHITE)
    ax.set_xlim(0, 1600)
    ax.set_ylim(0, 900)
    ax.axis('off')

    # Top Header Banner
    ax.text(60, 855, tag.upper(), fontsize=9, fontweight='bold', color="#2563EB", family='sans-serif', va='center')
    ax.text(60, 825, title, fontsize=18, fontweight='bold', color=TEXT_NAVY, family='sans-serif', va='center')
    if subtitle:
        ax.text(60, 800, subtitle, fontsize=10.5, color=TEXT_MUTED, family='sans-serif', va='center')

    # Header Divider Line
    line = plt.Line2D([60, 1540], [780, 780], color="#E2E8F0", linewidth=1.5)
    ax.add_line(line)

    # Footer Banner
    footer_line = plt.Line2D([60, 1540], [45, 45], color="#E2E8F0", linewidth=1.2)
    ax.add_line(footer_line)
    ax.text(60, 28, "AIOps Service Desk with Runbook Retrieval, Safe Automation & Human Approval", 
            fontsize=8.5, color=TEXT_MUTED, family='sans-serif', va='center')
    ax.text(1540, 28, "100% Local NLP • TF-IDF • Cosine Similarity • Zero External AI APIs • Simulation Mode", 
            fontsize=8.5, color=TEXT_MUTED, family='sans-serif', va='center', ha='right')

    return fig, ax

def draw_card(ax, x, y, w, h, title, items=None, theme="blue", badge=None, corner_radius=12, align='center', title_size=11, body_size=9):
    """
    Draws a styled rounded card with an optional badge and bulleted items.
    """
    t = THEMES[theme]
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={corner_radius}",
        facecolor=t["fill"],
        edgecolor=t["border"],
        linewidth=1.4,
        zorder=2
    )
    ax.add_patch(box)

    # Optional Badge at top right
    if badge:
        bx = x + w - 12
        by = y + h - 16
        bw = len(badge) * 6.5 + 16
        badge_box = patches.FancyBboxPatch(
            (bx - bw, by - 8), bw, 16,
            boxstyle="round,pad=0,rounding_size=6",
            facecolor=t["badge_bg"],
            edgecolor=t["border"],
            linewidth=0.8,
            zorder=3
        )
        ax.add_patch(badge_box)
        ax.text(bx - bw / 2, by, badge, fontsize=7.5, fontweight='bold', color=t["badge_text"],
                ha='center', va='center', family='sans-serif', zorder=4)

    # Content positioning
    if items:
        # Title near top
        ty = y + h - 22
        tx = x + 16 if align == 'left' else x + w / 2
        ha = 'left' if align == 'left' else 'center'
        ax.text(tx, ty, title, fontsize=title_size, fontweight='bold', color=t["text"],
                ha=ha, va='center', family='sans-serif', zorder=4)

        # Bullets / Subtext
        curr_y = ty - 20
        spacing = (h - 45) / max(len(items), 1)
        for item in items:
            prefix = "• " if align == 'left' else ""
            ax.text(tx, curr_y, prefix + item, fontsize=body_size, color=t["text"],
                    ha=ha, va='center', family='sans-serif', zorder=4)
            curr_y -= min(spacing, 18)
    else:
        # Title centered in card
        ax.text(x + w / 2, y + h / 2, title, fontsize=title_size, fontweight='bold', color=t["text"],
                ha='center', va='center', family='sans-serif', zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, label=None, color="#64748B", style="-|>", lw=1.5, ls="-", label_offset=(0, 10), label_color=TEXT_NAVY, label_bg=None, label_size=8.5):
    """
    Draws an arrow connection between two points with optional text label.
    """
    if style in ["-", "solid", "none"]:
        astyle = "-"
    else:
        astyle = f"{style},head_length=6,head_width=4"

    arrow = patches.FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=astyle,
        color=color,
        linewidth=lw,
        linestyle=ls,
        zorder=3
    )
    ax.add_patch(arrow)

    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        bbox_props = dict(boxstyle="round,pad=0.25", fc=label_bg if label_bg else BG_WHITE, ec="none", alpha=0.9) if label_bg else dict(boxstyle="round,pad=0.2", fc=BG_WHITE, ec="none", alpha=0.85)
        ax.text(mx, my, label, fontsize=label_size, fontweight='bold', color=label_color,
                ha='center', va='center', family='sans-serif', zorder=5, bbox=bbox_props)

def save_diagram(fig, filepath):
    """
    Saves canvas at 200 DPI into high-resolution PNG.
    """
    plt.tight_layout()
    fig.savefig(filepath, dpi=200, facecolor=BG_WHITE, edgecolor='none', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    print(f"Generated: {filepath}")
