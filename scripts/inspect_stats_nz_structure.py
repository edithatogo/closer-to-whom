"""Inspect a Stats NZ ADE SDMX structure response without fetching data."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect_structure(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    codelists = []
    for element in root.iter():
        if not element.tag.endswith("Codelist"):
            continue
        codes = []
        for code in element.iter():
            if code.tag.endswith("Code") and code.attrib.get("id"):
                codes.append(
                    {
                        "id": code.attrib["id"],
                        "names": [
                            (n.text or "").strip()
                            for n in code.iter()
                            if n.tag.endswith("Name") and n.text
                        ],
                    }
                )
        codelists.append(
            {
                "id": element.attrib.get("id"),
                "agency": element.attrib.get("agencyID"),
                "code_count": len(codes),
                "codes": codes,
            }
        )
    return {"codelist_count": len(codelists), "codelists": codelists}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("structure_xml", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()
    args.output_json.write_text(
        json.dumps(inspect_structure(args.structure_xml), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
