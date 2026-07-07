"""
lineage_visual.py
Génère une visualisation PNG du data lineage décrit dans data_lineage.md.
Le lineage s'arrête au Rapport consolidé car c'est la livraison finale
du module Data Quality (Personne 4).

Usage :
    python lineage/lineage_visual.py
    -> écrit lineage/data_lineage.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# =============================================================================
# CHEMIN DE SORTIE
# =============================================================================
CURRENT_FILE = os.path.abspath(__file__)
LINEAGE_DIR = os.path.dirname(CURRENT_FILE)
OUTPUT_PATH = os.path.join(LINEAGE_DIR, "data_lineage.png")

# (label, x, y, width, height, color)
# ← SUPPRIMÉ : PROCESSED ZONE, MODEL ZONE, SERVING ZONE
BOXES = [
    ("yield.csv\n(FAOSTAT)", 0.5, 6.5, 2.6, 0.8, "#cfe8ff"),
    ("Crop_recommendation.csv\n(Kaggle)", 5.0, 6.5, 3.0, 0.8, "#cfe8ff"),
    ("RAW ZONE\ndata/raw/*.csv", 3.0, 5.3, 3.2, 0.7, "#e8e8e8"),
    ("GATE 1\nData Quality Tests\n(completeness / validity / consistency)", 3.0, 3.9, 4.2, 0.9, "#ffe0b2"),
    ("GATE 2\nData Contract Validation\n(contract_validator.py)", 3.0, 2.6, 4.2, 0.8, "#ffe0b2"),
    ("Rapport consolidé\npipeline_report.json", 3.0, 1.4, 3.6, 0.7, "#ffcdd2"),
    # ← SUPPRIMÉ : PROCESSED ZONE
    # ← SUPPRIMÉ : MODEL ZONE
    # ← SUPPRIMÉ : SERVING ZONE
]

ARROWS = [
    (1.8, 6.5, 4.6, 5.65),
    (6.5, 6.5, 4.6, 5.65),
    (4.6, 5.3, 4.6, 4.8),
    (4.6, 3.9, 4.6, 3.4),
    (4.6, 2.6, 4.6, 2.1),
    # ← SUPPRIMÉ : flèche vers PROCESSED ZONE
    # ← SUPPRIMÉ : flèche vers MODEL ZONE
    # ← SUPPRIMÉ : flèche vers SERVING ZONE
]


def draw_box(ax, label, x, y, w, h, color):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.08",
        linewidth=1.2, edgecolor="#333333", facecolor=color,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
             fontsize=9, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2):
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=14,
        color="#555555", linewidth=1.2,
    )
    ax.add_patch(arrow)


def main():
    fig, ax = plt.subplots(figsize=(9, 6.5))  # ← Réduit la hauteur
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 7.5)  # ← Réduit l'axe Y
    ax.axis("off")
    ax.set_title("Data Lineage — Module Data Quality (Personne 4)", 
                 fontsize=13, fontweight="bold")

    for label, x, y, w, h, color in BOXES:
        draw_box(ax, label, x, y, w, h, color)

    for x1, y1, x2, y2 in ARROWS:
        draw_arrow(ax, x1, y1, x2, y2)

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"Diagramme de lineage écrit dans : {OUTPUT_PATH}")


if __name__ == "__main__":
    main()