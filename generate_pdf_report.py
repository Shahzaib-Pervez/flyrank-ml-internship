"""
===============================================================================
GENERATE_PDF_REPORT.PY
Search Intelligence Capstone — AI Fluency Week 03 PDF Generator
===============================================================================
Generates AI_Fluency_Week03_Curate_Your_Images.pdf using matplotlib.backends.backend_pdf.
"""

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def create_assignment_pdf():
    pdf_filename = "AI_Fluency_Week03_Curate_Your_Images.pdf"
    
    with PdfPages(pdf_filename) as pdf:
        # -------------------------------------------------------------
        # PAGE 1: Title, Executive Summary & Content Map Table
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Header & Metadata
        ax.text(0.05, 0.95, "AI FLUENCY TRACK — WEEK 03 ASSIGNMENT", fontsize=10, fontweight='bold', color='#2563eb')
        ax.text(0.05, 0.92, "Curate Your Images: Visual Discernment & Asset Strategy", fontsize=18, fontweight='bold', color='#0f172a')
        ax.text(0.05, 0.895, "Author: Shahzaib Pervez  |  Context: ML Portfolio  |  Date: August 2026", fontsize=9, color='#64748b')
        ax.plot([0.05, 0.95], [0.88, 0.88], color='#2563eb', lw=2)

        # Core Philosophy Box
        rect = plt.Rectangle((0.05, 0.77), 0.90, 0.09, facecolor='#f8fafc', edgecolor='#2563eb', lw=1.5)
        ax.add_patch(rect)
        ax.text(0.07, 0.84, "CORE PHILOSOPHY & PRINCIPLE", fontsize=10, fontweight='bold', color='#0f172a')
        summary_text = (
            "AI permits infinite image generation in seconds, making visual judgment and curation far more\n"
            "critical than raw generation. The objective is to use real screenshots for proof of technical work,\n"
            "a real photograph for personal identity, and strictly cohesive AI generations for non-subject connective tissue."
        )
        ax.text(0.07, 0.785, summary_text, fontsize=9, color='#334155', linespacing=1.2)

        # Section 1 Header & Inventory Table
        ax.text(0.05, 0.73, "1. Portfolio Content Map & Image Inventory", fontsize=13, fontweight='bold', color='#0f172a')
        
        table_data = [
            ["Portfolio Section", "Visual Need / Purpose", "Sourcing Choice", "Filename"],
            ["Hero Header", "Connective dark tech background texture", "AI Generated", "hero_dark_network_mesh.png"],
            ["About Profile", "Personal identity & human credibility", "Real Photo", "shahzaib_profile_headshot.jpg"],
            ["Project #1 (FlyRank)", "Proof of work: ROC curve & DuckDB pipeline", "Real Capture", "proof_flyrank_roc_pipeline.png"],
            ["Project #2 (Paper UI)", "Proof of work: Deployed web paper interface", "Real Capture", "proof_research_paper_ui.png"],
            ["Skill Badges", "Minimal, consistent skill icon set", "AI Generated", "icon_set_minimal.svg"]
        ]
        
        table = ax.table(cellText=table_data, loc='upper center', bbox=[0.05, 0.44, 0.90, 0.26])
        table.auto_set_font_size(False)
        table.set_fontsize(8.5)
        
        # Style table headers and cells
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_facecolor('#0f172a')
                cell.set_text_props(color='#ffffff', fontweight='bold')
            else:
                if col == 2:
                    if "Real" in cell.get_text().get_text():
                        cell.set_facecolor('#d1fae5')
                        cell.set_text_props(color='#065f46', fontweight='bold')
                    else:
                        cell.set_facecolor('#ede9fe')
                        cell.set_text_props(color='#5b21b6', fontweight='bold')
                elif row % 2 == 0:
                    cell.set_facecolor('#f8fafc')

        # Section 2: Real Captures vs AI Rationale
        ax.text(0.05, 0.40, "2. Rationale: Where Real Captures Beat AI", fontsize=13, fontweight='bold', color='#0f172a')
        
        rat_1 = (
            "A. Real Captures for Technical Work (Proof of Work):\n"
            "AI-generated UI mockups look synthetic and hallucinate fake metric labels or broken code typography.\n"
            "In technical portfolio reviews, hiring managers seek verifiable proof. Real, clean screenshots of actual\n"
            "DuckDB queries, scikit-learn metrics, and web UI layouts establish instant credibility that AI destroys."
        )
        ax.text(0.05, 0.30, rat_1, fontsize=8.5, color='#1e293b', linespacing=1.2)

        rat_2 = (
            "B. Real Photography for Personal Profile:\n"
            "An AI-generated avatar creates an immediate 'uncanny valley' response and signals dishonesty regarding\n"
            "identity. Personal trust and human connection require an authentic photograph."
        )
        ax.text(0.05, 0.20, rat_2, fontsize=8.5, color='#1e293b', linespacing=1.2)

        rat_3 = (
            "C. AI Generation for Connective Tissue & Hero Texture:\n"
            "AI was used exclusively for the hero ambient mesh and skill icons to maintain exact color harmony\n"
            "(dark slate #0f172a with cyan/indigo accent mesh) without competing for visual attention."
        )
        ax.text(0.05, 0.10, rat_3, fontsize=8.5, color='#1e293b', linespacing=1.2)

        ax.text(0.5, 0.03, "Page 1 of 2", fontsize=8, color='#94a3b8', ha='center')
        pdf.savefig(fig)
        plt.close()

        # -------------------------------------------------------------
        # PAGE 2: Ruthless Curation, Rejection Analysis & Rubric
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')

        ax.text(0.05, 0.95, "3. Ruthless Curation & Rejection Analysis (The Discernment Test)", fontsize=13, fontweight='bold', color='#0f172a')
        ax.text(0.05, 0.925, "Discernment is defined by what you choose NOT to include. Below is the evaluation of rejected AI generations:", fontsize=8.5, color='#64748b')

        # Rejection 1 Box
        r1_box = plt.Rectangle((0.05, 0.76), 0.90, 0.14, facecolor='#fef2f2', edgecolor='#dc2626', lw=1.2)
        ax.add_patch(r1_box)
        ax.text(0.07, 0.87, "REJECTED CANDIDATE #1: 'Holographic Cyberpunk Brain Dashboard' (Prompt Iteration 2)", fontsize=9.5, fontweight='bold', color='#991b1b')
        r1_text = (
            "Prompt: 'Futuristic glowing brain made of neon blue data circuits floating over dark cybernetic background.'\n"
            "Why Rejected: Experienced extreme aesthetic cliché and high visual noise. The neon pink/cyan glow clashed\n"
            "harshly with the portfolio's minimalist dark-mode design system (#0f172a slate). Floating sci-fi brain imagery\n"
            "communicates amateurish tropes rather than serious data engineering capability."
        )
        ax.text(0.07, 0.775, r1_text, fontsize=8.5, color='#7f1d1d', linespacing=1.2)

        # Rejection 2 Box
        r2_box = plt.Rectangle((0.05, 0.60), 0.90, 0.14, facecolor='#fef2f2', edgecolor='#dc2626', lw=1.2)
        ax.add_patch(r2_box)
        ax.text(0.07, 0.71, "REJECTED CANDIDATE #2: 'Hyper-realistic 3D Glass Orbs with Code' (Prompt Iteration 5)", fontsize=9.5, fontweight='bold', color='#991b1b')
        r2_text = (
            "Prompt: 'Minimalist glass sphere reflecting python code lines, realistic lighting, dramatic depth of field.'\n"
            "Why Rejected: The dramatic depth of field and specular highlights created an inconsistent 'pile' alongside\n"
            "the portfolio cards. The strong specular reflections drew focus away from project headings, breaking visual hierarchy."
        )
        ax.text(0.07, 0.615, r2_text, fontsize=8.5, color='#7f1d1d', linespacing=1.2)

        # Keeper Box
        k_box = plt.Rectangle((0.05, 0.44), 0.90, 0.14, facecolor='#f0fdf4', edgecolor='#059669', lw=1.2)
        ax.add_patch(k_box)
        ax.text(0.07, 0.55, "THE KEEPER: 'Subdued Dark Vector Network Mesh' (Prompt Iteration 8)", fontsize=9.5, fontweight='bold', color='#166534')
        k_text = (
            "Prompt: 'Clean abstract dark slate background, subtle deep blue and cyan network nodes connected by ultra-fine\n"
            "faint gradient lines, flat modern vector style, no noise, 16:9 ratio.'\n"
            "Why Kept: Maintains perfect visual harmony with site CSS tokens (#0f172a slate background, #06b6d4 cyan accents).\n"
            "The low-contrast gradient lines sit softly behind hero typography, forming a cohesive set."
        )
        ax.text(0.07, 0.455, k_text, fontsize=8.5, color='#14532d', linespacing=1.2)

        # Section 4: Rubric Evaluation
        ax.text(0.05, 0.39, "4. Pass / Revise Self-Assessment Rubric", fontsize=13, fontweight='bold', color='#0f172a')
        
        rubric_data = [
            ["Rubric Requirement", "Status", "Evaluation & Compliance Evidence"],
            ["1. Content Mapping", "PASS", "Every image maps to a specific portfolio section with clear purpose."],
            ["2. Real Work Captures", "PASS", "Technical work is proven using real, un-hallucinated screenshots."],
            ["3. AI Style Consistency", "PASS", "All connective AI assets share one consistent dark slate/cyan visual set."],
            ["4. Personal Identity", "PASS", "Authentic photograph used for profile/author identity."],
            ["5. Genuine Discernment", "PASS", "Rejection notes detail explicit design rules (hierarchy, noise, contrast)."]
        ]

        rubric_table = ax.table(cellText=rubric_data, loc='upper center', bbox=[0.05, 0.12, 0.90, 0.24])
        rubric_table.auto_set_font_size(False)
        rubric_table.set_fontsize(8)

        for (row, col), cell in rubric_table.get_celld().items():
            if row == 0:
                cell.set_facecolor('#0f172a')
                cell.set_text_props(color='#ffffff', fontweight='bold')
            else:
                if col == 1:
                    cell.set_facecolor('#dcfce7')
                    cell.set_text_props(color='#15803d', fontweight='bold')
                elif row % 2 == 0:
                    cell.set_facecolor('#f8fafc')

        ax.text(0.5, 0.03, "Page 2 of 2 — AI Fluency Internship Track", fontsize=8, color='#94a3b8', ha='center')
        pdf.savefig(fig)
        plt.close()

    print(f"[PDF Generated] {pdf_filename}")
    return pdf_filename

if __name__ == "__main__":
    create_assignment_pdf()
