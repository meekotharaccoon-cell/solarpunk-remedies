"""
remedies_agent.py — SolarPunk Remedies autonomous agent.

Maintains a catalog of natural yard remedies, generates guides,
tracks Gumroad publication status, and produces seasonal recommendations.
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

# Allow running from repo root or agent/ directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guide_generator import (
    generate_free_guide,
    generate_premium_guide,
    generate_seasonal_guide,
    generate_multi_remedy_guide,
    save_guide,
)


CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "catalog.json")
GUIDES_DIR = os.path.join(os.path.dirname(__file__), "..", "guides")
STATUS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "publish_status.json")

SEASONS_BY_MONTH = {
    1: "winter", 2: "winter", 3: "spring",
    4: "spring", 5: "spring", 6: "summer",
    7: "summer", 8: "summer", 9: "fall",
    10: "fall", 11: "fall", 12: "winter",
}


class RemediesAgent:
    """Autonomous agent for managing the SolarPunk Remedies catalog and guides."""

    def __init__(self, catalog_path: Optional[str] = None):
        self.catalog_path = catalog_path or CATALOG_PATH
        self.catalog = self._load_catalog()
        self.publish_status = self._load_publish_status()

    def _load_catalog(self) -> dict:
        """Load the remedy catalog from disk."""
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "1.0.0", "last_updated": "", "remedies": []}

    def _save_catalog(self):
        """Persist the catalog back to disk."""
        self.catalog["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        os.makedirs(os.path.dirname(self.catalog_path), exist_ok=True)
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)

    def _load_publish_status(self) -> dict:
        """Load the Gumroad publication tracking file."""
        if os.path.exists(STATUS_PATH):
            with open(STATUS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"published": [], "last_check": ""}

    def _save_publish_status(self):
        """Persist publication status."""
        self.publish_status["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.publish_status, f, indent=2)

    @property
    def remedies(self) -> list:
        return self.catalog.get("remedies", [])

    def get_remedy(self, remedy_id: str) -> Optional[dict]:
        """Look up a single remedy by its ID."""
        for r in self.remedies:
            if r["id"] == remedy_id:
                return r
        return None

    def list_remedies(self) -> list:
        """Return a summary list of all remedies (id, name, difficulty)."""
        return [
            {"id": r["id"], "name": r["name"], "difficulty": r.get("difficulty", "unknown")}
            for r in self.remedies
        ]

    def add_remedy(self, remedy: dict):
        """Add a new remedy to the catalog. Requires at minimum: id, name, plants, preparation_steps."""
        required = {"id", "name", "plants", "preparation_steps"}
        missing = required - set(remedy.keys())
        if missing:
            raise ValueError(f"Remedy missing required fields: {missing}")
        # Avoid duplicates
        if self.get_remedy(remedy["id"]):
            raise ValueError(f"Remedy '{remedy['id']}' already exists in catalog.")
        remedy.setdefault("uses", [])
        remedy.setdefault("safety_notes", "Consult a healthcare provider before use.")
        remedy.setdefault("season", "year-round")
        remedy.setdefault("difficulty", "beginner")
        remedy.setdefault("gumroad_published", False)
        self.catalog["remedies"].append(remedy)
        self._save_catalog()
        print(f"[+] Added remedy: {remedy['name']}")

    def generate_guides(self, remedy_id: Optional[str] = None, output_dir: Optional[str] = None):
        """Generate free and premium guides for one or all remedies."""
        out = output_dir or GUIDES_DIR
        targets = [self.get_remedy(remedy_id)] if remedy_id else self.remedies
        targets = [t for t in targets if t is not None]

        generated = 0
        for remedy in targets:
            rid = remedy["id"]
            # Free version
            free_path = os.path.join(out, "free", f"{rid}.md")
            save_guide(generate_free_guide(remedy), free_path)
            # Premium version
            premium_path = os.path.join(out, "premium", f"{rid}.md")
            save_guide(generate_premium_guide(remedy), premium_path)
            generated += 1
            print(f"  [guide] {remedy['name']} -> free + premium")

        print(f"[+] Generated guides for {generated} remedies in {out}")
        return generated

    def get_seasonal_recommendations(self, month: Optional[int] = None) -> dict:
        """Return remedies appropriate for the current (or specified) season."""
        month = month or datetime.now().month
        season = SEASONS_BY_MONTH.get(month, "spring")
        matching = []
        for r in self.remedies:
            r_season = r.get("season", "").lower()
            if season in r_season or "year-round" in r_season:
                matching.append({
                    "id": r["id"],
                    "name": r["name"],
                    "uses": r.get("uses", []),
                    "difficulty": r.get("difficulty", "unknown"),
                })
        return {
            "season": season,
            "month": month,
            "count": len(matching),
            "remedies": matching,
        }

    def generate_seasonal_guide(self, month: Optional[int] = None, output_dir: Optional[str] = None):
        """Generate a seasonal recommendation guide."""
        month = month or datetime.now().month
        season = SEASONS_BY_MONTH.get(month, "spring")
        out = output_dir or GUIDES_DIR
        guide_content = generate_seasonal_guide(self.remedies, season)
        filepath = os.path.join(out, f"seasonal-{season}.md")
        save_guide(guide_content, filepath)
        print(f"[+] Seasonal guide for {season} -> {filepath}")
        return filepath

    def get_unpublished(self) -> list:
        """Return remedies not yet published to Gumroad."""
        published_ids = set(self.publish_status.get("published", []))
        return [
            {"id": r["id"], "name": r["name"]}
            for r in self.remedies
            if r["id"] not in published_ids and not r.get("gumroad_published", False)
        ]

    def mark_published(self, remedy_id: str):
        """Mark a remedy as published to Gumroad."""
        if remedy_id not in self.publish_status["published"]:
            self.publish_status["published"].append(remedy_id)
        # Also update the catalog entry
        remedy = self.get_remedy(remedy_id)
        if remedy:
            remedy["gumroad_published"] = True
            self._save_catalog()
        self._save_publish_status()
        print(f"[+] Marked '{remedy_id}' as published to Gumroad.")

    def catalog_stats(self) -> dict:
        """Return summary statistics about the catalog."""
        total = len(self.remedies)
        published = sum(1 for r in self.remedies if r.get("gumroad_published", False))
        difficulties = {}
        for r in self.remedies:
            d = r.get("difficulty", "unknown")
            difficulties[d] = difficulties.get(d, 0) + 1
        return {
            "total_remedies": total,
            "published_to_gumroad": published,
            "unpublished": total - published,
            "by_difficulty": difficulties,
            "last_updated": self.catalog.get("last_updated", "never"),
        }

    def run(self):
        """Main agent loop: load catalog, generate guides, print seasonal recs."""
        print("=" * 60)
        print("  SolarPunk Remedies Agent")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        # Stats
        stats = self.catalog_stats()
        print(f"Catalog: {stats['total_remedies']} remedies")
        print(f"  Published to Gumroad: {stats['published_to_gumroad']}")
        print(f"  Unpublished: {stats['unpublished']}")
        print(f"  By difficulty: {stats['by_difficulty']}")
        print()

        # Generate all guides
        print("Generating guides...")
        self.generate_guides()
        print()

        # Seasonal recommendations
        recs = self.get_seasonal_recommendations()
        print(f"Season: {recs['season']} ({recs['count']} remedies available)")
        for r in recs["remedies"]:
            uses_str = ", ".join(r["uses"][:3])
            print(f"  - {r['name']} ({r['difficulty']}) — {uses_str}")
        print()

        # Generate seasonal guide
        self.generate_seasonal_guide()
        print()

        # Unpublished remedies
        unpub = self.get_unpublished()
        if unpub:
            print(f"Ready to publish ({len(unpub)} remedies):")
            for u in unpub:
                print(f"  - {u['name']} (id: {u['id']})")
        else:
            print("All remedies published to Gumroad.")
        print()

        print("Agent run complete.")
        print("=" * 60)


if __name__ == "__main__":
    agent = RemediesAgent()
    agent.run()
