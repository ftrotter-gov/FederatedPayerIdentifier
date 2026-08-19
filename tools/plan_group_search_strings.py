#!/usr/bin/env python3
"""Derive plan-level and plan-group-level search strings from plan_name fields.

For each plan_group in each given well-known payer file, this tool:

  1. Adds a "plan_level_string_search_matches" array to every plan identifier
     entry that has a plan_name.  The array documents the per-plan string
     matches: the plan_name itself, plus the cruft-stripped version of the
     name (parenthetical suffixes like "(PPO)", "(HMO)", "(HMO-POS D-SNP)"
     removed) when that differs from the original.

  2. Adds a "plan_group_string_search_match" array to the plan_group,
     containing every cruft-stripped plan name that REPEATS (appears two or
     more times, case-insensitive) across the plan_names in that group —
     e.g. "Aetna Medicare Enhanced" repeats once "(PPO)" and "(HMO)" are
     stripped from "Aetna Medicare Enhanced (PPO)" and
     "Aetna Medicare Enhanced (HMO)".

Case changes are ignored when matching (so "Aetna" and "aetna" match); the
first-seen casing is used in the output.

Usage:
    python tools/plan_group_search_strings.py <well_known_file.json> [...]
"""

import json
import re
import sys

# Parenthetical cruft such as "(PPO)", "(HMO)", "(HMO-POS D-SNP)", etc.
_PAREN_CRUFT_PATTERN = re.compile(r"\([^)]*\)")


class PlanGroupSearchStrings:
    """Namespace class holding the analysis steps as static methods."""

    @staticmethod
    def strip_plan_name_cruft(*, plan_name):
        """Remove parenthetical cruft like "(PPO)" / "(HMO)" and collapse whitespace."""
        cleaned = _PAREN_CRUFT_PATTERN.sub(" ", plan_name)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @staticmethod
    def _annotate_plan_group(*, plan_group):
        """Add plan-level and group-level search strings to one plan_group.

        Returns the number of repeated group-level strings found.
        """
        # cleaned-name (lowercased) -> {"count": int, "first_casing": str}
        cleaned_name_stats = {}

        for plan_identifier_entry in plan_group.get("plan_identifiers", []):
            plan_name = plan_identifier_entry.get("plan_name")
            if not plan_name:
                continue

            cleaned_name = PlanGroupSearchStrings.strip_plan_name_cruft(plan_name=plan_name)

            # Per-plan search strings: the name itself plus its cleaned form.
            plan_search_matches = [plan_name]
            if cleaned_name and cleaned_name.lower() != plan_name.lower():
                plan_search_matches.append(cleaned_name)
            plan_identifier_entry["plan_level_string_search_matches"] = plan_search_matches

            # Tally cleaned names for group-level repetition analysis.
            if cleaned_name:
                cleaned_key = cleaned_name.lower()
                if cleaned_key not in cleaned_name_stats:
                    cleaned_name_stats[cleaned_key] = {"count": 0, "first_casing": cleaned_name}
                cleaned_name_stats[cleaned_key]["count"] += 1

        repeated_strings = sorted(
            (stats["first_casing"] for stats in cleaned_name_stats.values() if stats["count"] >= 2),
            key=str.lower,
        )
        if repeated_strings:
            plan_group["plan_group_string_search_match"] = repeated_strings
        return len(repeated_strings)

    @staticmethod
    def _reorder_plan_group_keys(*, plan_group):
        """Return a plan_group dict with keys in the documented order:
        plan_identifiers, plan_group_string_search_match, plan_endpoints, then
        any other keys in their original order."""
        preferred_key_order = ["plan_identifiers", "plan_group_string_search_match", "plan_endpoints"]
        reordered = {}
        for key in preferred_key_order:
            if key in plan_group:
                reordered[key] = plan_group[key]
        for key, value in plan_group.items():
            if key not in reordered:
                reordered[key] = value
        return reordered

    @staticmethod
    def process_file(*, file_path):
        """Annotate every plan_group in one well-known payer file."""
        with open(file_path, encoding="utf-8") as json_file:
            doc = json.load(json_file)

        total_repeated_strings = 0
        annotated_groups = []
        for plan_group in doc.get("plan_groups", []):
            total_repeated_strings += PlanGroupSearchStrings._annotate_plan_group(plan_group=plan_group)
            annotated_groups.append(PlanGroupSearchStrings._reorder_plan_group_keys(plan_group=plan_group))
        doc["plan_groups"] = annotated_groups

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(doc, json_file, indent=2)
            json_file.write("\n")

        print(f"{file_path}: {len(annotated_groups)} plan_group(s) annotated, "
              f"{total_repeated_strings} repeated group-level string(s) found")

    @staticmethod
    def run(*, file_paths):
        for file_path in file_paths:
            PlanGroupSearchStrings.process_file(file_path=file_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("plan_group_search_strings.py Error: no input files given. "
              "Usage: python tools/plan_group_search_strings.py <file.json> [...]")
        sys.exit(1)
    PlanGroupSearchStrings.run(file_paths=sys.argv[1:])