"""
guide_generator.py — SolarPunk Remedies guide creation engine.

Takes remedy entries from catalog.json and generates formatted markdown guides
in both free (basic) and premium (detailed) versions.
"""

import json
import os
from datetime import datetime
from typing import Optional


DISCLAIMER = """
> **IMPORTANT DISCLAIMER**
>
> This guide is for **educational purposes only** and is not a substitute for
> professional medical advice, diagnosis, or treatment. Always consult a qualified
> healthcare provider before using any herbal remedy, especially if you are pregnant,
> nursing, taking medications, or have a medical condition.
>
> Never consume a plant you cannot positively identify. When in doubt, don't.
"""

SOLARPUNK_FOOTER = """
---

*From your yard to your medicine cabinet — 100% organic, plant-based, SolarPunk.*

*Made with care by [SolarPunk Remedies](https://meekotharaccoon-cell.github.io/solarpunk-remedies).*
"""


def generate_free_guide(remedy: dict) -> str:
    """Generate a basic (free) markdown guide for a single remedy.

    The free version includes the remedy name, a brief description, basic
    preparation overview, and the safety disclaimer. It omits detailed
    step-by-step instructions and seasonal notes to encourage premium purchase.
    """
    lines = []
    lines.append(f"# {remedy['name']}")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"**Plants used:** {', '.join(remedy['plants'])}")
    lines.append(f"**Difficulty:** {remedy.get('difficulty', 'beginner')}")
    lines.append(f"**Best season:** {remedy.get('season', 'year-round')}")
    lines.append("")
    lines.append("## What it helps with")
    lines.append("")
    for use in remedy.get("uses", []):
        lines.append(f"- {use.capitalize()}")
    lines.append("")
    lines.append("## Basic preparation")
    lines.append("")
    steps = remedy.get("preparation_steps", [])
    if len(steps) >= 3:
        lines.append(f"1. {steps[0]}")
        lines.append(f"2. {steps[1]}")
        lines.append(f"3. {steps[2]}")
        lines.append("")
        lines.append(
            f"*...full {len(steps)}-step preparation guide available in the "
            f"[premium version](https://gumroad.com) for $1.*"
        )
    else:
        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## Safety notes")
    lines.append("")
    lines.append(remedy.get("safety_notes", "Consult a healthcare provider before use."))
    lines.append("")
    lines.append(SOLARPUNK_FOOTER)
    return "\n".join(lines)


def generate_premium_guide(remedy: dict) -> str:
    """Generate a detailed (premium) markdown guide for a single remedy.

    The premium version includes full step-by-step preparation, yield and
    shelf life info, seasonal details, and extended safety information.
    """
    lines = []
    lines.append(f"# {remedy['name']} — Complete Guide")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("1. [Overview](#overview)")
    lines.append("2. [Plants & Identification](#plants--identification)")
    lines.append("3. [Full Preparation Steps](#full-preparation-steps)")
    lines.append("4. [Uses & Applications](#uses--applications)")
    lines.append("5. [Yield & Storage](#yield--storage)")
    lines.append("6. [Seasonal Notes](#seasonal-notes)")
    lines.append("7. [Safety Information](#safety-information)")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(f"**Difficulty:** {remedy.get('difficulty', 'beginner').capitalize()}")
    lines.append(f"**Best season:** {remedy.get('season', 'year-round')}")
    lines.append(f"**Yield:** {remedy.get('yield', 'varies')}")
    lines.append(f"**Shelf life:** {remedy.get('shelf_life', 'varies')}")
    lines.append("")

    # Plants
    lines.append("## Plants & Identification")
    lines.append("")
    for plant in remedy.get("plants", []):
        lines.append(f"- **{plant}**")
    lines.append("")
    lines.append(
        "Always positively identify plants before harvesting. Use a reliable "
        "field guide or consult an experienced forager. When wildcrafting, harvest "
        "sustainably — never take more than 1/3 of a plant stand."
    )
    lines.append("")

    # Full preparation
    lines.append("## Full Preparation Steps")
    lines.append("")
    for i, step in enumerate(remedy.get("preparation_steps", []), 1):
        lines.append(f"**Step {i}.** {step}")
        lines.append("")
    lines.append("")

    # Uses
    lines.append("## Uses & Applications")
    lines.append("")
    for use in remedy.get("uses", []):
        lines.append(f"- {use.capitalize()}")
    lines.append("")

    # Yield & Storage
    lines.append("## Yield & Storage")
    lines.append("")
    lines.append(f"- **Expected yield:** {remedy.get('yield', 'varies')}")
    lines.append(f"- **Shelf life:** {remedy.get('shelf_life', 'varies')}")
    lines.append("- Store in clean, airtight glass containers away from direct sunlight.")
    lines.append("- Label everything with contents and date of preparation.")
    lines.append("")

    # Seasonal notes
    lines.append("## Seasonal Notes")
    lines.append("")
    lines.append(f"**Best time:** {remedy.get('season', 'year-round')}")
    lines.append("")
    _add_seasonal_tips(lines, remedy)
    lines.append("")

    # Safety
    lines.append("## Safety Information")
    lines.append("")
    lines.append(remedy.get("safety_notes", "Consult a healthcare provider before use."))
    lines.append("")
    lines.append("**General safety practices:**")
    lines.append("- Start with small doses to check for allergic reactions.")
    lines.append("- Keep a record of what you take and any effects.")
    lines.append("- Do not combine multiple herbal remedies without research.")
    lines.append("- Seek professional medical help for serious conditions.")
    lines.append("- If symptoms worsen or persist, stop use and consult a doctor.")
    lines.append("")

    lines.append(SOLARPUNK_FOOTER)
    return "\n".join(lines)


def _add_seasonal_tips(lines: list, remedy: dict):
    """Add season-specific foraging and preparation tips."""
    season = remedy.get("season", "").lower()
    if "spring" in season:
        lines.append(
            "- Spring is prime harvest time. Watch for new growth after the last frost."
        )
        lines.append(
            "- Young plants and fresh shoots have the highest concentration of active compounds."
        )
    if "summer" in season:
        lines.append(
            "- Harvest in the morning after dew has dried but before the midday heat."
        )
        lines.append(
            "- Flowers are best picked just as they fully open."
        )
    if "fall" in season:
        lines.append(
            "- Fall roots contain stored energy and concentrated compounds."
        )
        lines.append(
            "- Harvest after the aerial parts begin to die back."
        )
    if "year-round" in season:
        lines.append(
            "- Available year-round, but potency may vary by season."
        )
        lines.append(
            "- Stock up on dried material when the plant is at peak vitality."
        )


def generate_multi_remedy_guide(remedies: list, title: str = "SolarPunk Remedies Collection") -> str:
    """Generate a combined guide covering multiple remedies with a table of contents."""
    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"*Generated on {datetime.now().strftime('%B %d, %Y')}*")
    lines.append("")
    lines.append(DISCLAIMER)
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for i, remedy in enumerate(remedies, 1):
        anchor = remedy["name"].lower().replace(" ", "-").replace("'", "")
        lines.append(f"{i}. [{remedy['name']}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Each remedy
    for remedy in remedies:
        lines.append(f"## {remedy['name']}")
        lines.append("")
        lines.append(f"**Plants:** {', '.join(remedy['plants'])}")
        lines.append(f"**Difficulty:** {remedy.get('difficulty', 'beginner').capitalize()}")
        lines.append(f"**Season:** {remedy.get('season', 'year-round')}")
        lines.append("")
        lines.append("### Preparation")
        lines.append("")
        for j, step in enumerate(remedy.get("preparation_steps", []), 1):
            lines.append(f"{j}. {step}")
        lines.append("")
        lines.append("### Uses")
        lines.append("")
        for use in remedy.get("uses", []):
            lines.append(f"- {use.capitalize()}")
        lines.append("")
        lines.append(f"**Safety:** {remedy.get('safety_notes', 'Consult a healthcare provider.')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(SOLARPUNK_FOOTER)
    return "\n".join(lines)


def generate_seasonal_guide(remedies: list, season: str) -> str:
    """Generate a guide containing only remedies appropriate for the given season."""
    season_lower = season.lower()
    matching = [r for r in remedies if season_lower in r.get("season", "").lower() or "year-round" in r.get("season", "").lower()]
    if not matching:
        return f"# No remedies found for {season}\n\nCheck back as the catalog grows.\n"
    title = f"SolarPunk Remedies — {season.capitalize()} Guide"
    return generate_multi_remedy_guide(matching, title)


def save_guide(content: str, filepath: str):
    """Write a guide to a file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    catalog_path = os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        remedies = catalog.get("remedies", [])
        if remedies:
            guide = generate_free_guide(remedies[0])
            print(guide[:500])
            print(f"\n... generated {len(guide)} chars for free guide: {remedies[0]['name']}")
    else:
        print(f"Catalog not found at {catalog_path}")
