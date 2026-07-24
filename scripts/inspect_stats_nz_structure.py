"""Inspect a Stats NZ ADE SDMX structure response without fetching data."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect_structure(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    codelists = []
    composite_code_ids: set[str] = set()
    component_code_ids: set[str] = set()
    for element in root.iter():
        if not element.tag.endswith("Codelist"):
            continue
        codes = []
        for code in element.iter():
            if code.tag.endswith("Code") and code.attrib.get("id"):
                code_id = code.attrib["id"]
                rules = [
                    (annotation.text or "").strip()
                    for annotation in code.iter()
                    if annotation.tag.endswith("AnnotationTitle") and annotation.text
                ]
                if rules:
                    composite_code_ids.add(code_id)
                    for rule in rules:
                        component_code_ids.update(rule.split("+"))
                codes.append(
                    {
                        "id": code_id,
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
    area = next((item for item in codelists if item["id"] == "CL_AREA_POPES_SUB_004"), None)
    area_ids = {code["id"] for code in area["codes"]} if area else set()
    return {
        "codelist_count": len(codelists),
        "codelists": codelists,
        "area_composite_code_ids": sorted(composite_code_ids & area_ids),
        "area_component_code_ids": sorted(component_code_ids & area_ids),
        "area_leaf_code_ids": sorted((area_ids - composite_code_ids) & component_code_ids),
    }


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
