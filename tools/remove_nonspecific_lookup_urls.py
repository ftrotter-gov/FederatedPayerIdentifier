#!/usr/bin/env python3
"""Remove non-specific lookup_url fields from well-known payer identifier entries.

A lookup_url is kept only when it points at the actual specific entity — i.e.
when the identifier value itself appears inside the URL (for example
https://lei.bloomberg.com/leis/view/5493000TJJYWT3N7J985 for the LEI value
5493000TJJYWT3N7J985, or https://www.tdi.texas.gov/hmo/profiles/68775.html for
the state-prefixed STATE_DOI_ID value TX-68775).  Generic lookup URLs (PDF
lists, spreadsheets, public-use files, etc.) are removed.

Usage:
    python tools/remove_nonspecific_lookup_urls.py <well_known_file.json> [...]
"""

import json
import re
import sys

_STATE_PREFIX_PATTERN = re.compile(r"^[A-Z]{2}-(.+)$")


class LookupUrlCleaner:
    """Namespace class holding the cleanup steps as static methods."""

    @staticmethod
    def _url_is_specific_to_value(*, lookup_url, identifier_value):
        """Return True when the identifier value appears inside the URL.

        For state-prefixed values like "TX-68775" the unprefixed value
        ("68775") also counts, since state DOI profile pages use the raw
        number.  Comparison is case-insensitive.
        """
        if not lookup_url:
            return False
        url_lower = lookup_url.lower()
        candidate_values = {identifier_value.lower()}
        state_prefix_match = _STATE_PREFIX_PATTERN.match(identifier_value)
        if state_prefix_match:
            candidate_values.add(state_prefix_match.group(1).lower())
        return any(candidate in url_lower for candidate in candidate_values)

    @staticmethod
    def clean_file(*, file_path):
        """Remove non-specific lookup_url fields from one well-known file."""
        with open(file_path, encoding="utf-8") as json_file:
            doc = json.load(json_file)

        removed_count = 0
        kept_count = 0
        for identifier_entry in doc.get("identifier", []):
            if "lookup_url" not in identifier_entry:
                continue
            url_is_specific = LookupUrlCleaner._url_is_specific_to_value(
                lookup_url=identifier_entry["lookup_url"],
                identifier_value=identifier_entry["value"],
            )
            if url_is_specific:
                kept_count += 1
            else:
                del identifier_entry["lookup_url"]
                removed_count += 1

        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(doc, json_file, indent=2)
            json_file.write("\n")

        print(f"{file_path}: removed {removed_count} generic lookup_url(s), kept {kept_count} entity-specific one(s)")

    @staticmethod
    def run(*, file_paths):
        for file_path in file_paths:
            LookupUrlCleaner.clean_file(file_path=file_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("remove_nonspecific_lookup_urls.py Error: no input files given. "
              "Usage: python tools/remove_nonspecific_lookup_urls.py <file.json> [...]")
        sys.exit(1)
    LookupUrlCleaner.run(file_paths=sys.argv[1:])