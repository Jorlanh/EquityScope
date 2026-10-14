from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "wiid_2002_2026.csv"
OUTPUT = ROOT / "data" / "processed" / "country_group_membership.csv"


def clean(value: str | None) -> str:
    if value is None:
        return ""
    value = value.strip()
    if value.lower() in {"", "nan", "nat", "none", "null"}:
        return ""
    return value


def group_code(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", "_", ascii_value.upper()).strip("_")


def most_common(values: list[str]) -> str:
    valid = [value for value in values if value]
    if not valid:
        return ""
    return Counter(valid).most_common(1)[0][0]


def add_group(
    rows: list[dict[str, str]],
    country_code: str,
    country_name: str,
    group_type: str,
    group_name: str,
    notes: str,
) -> None:
    if not group_name:
        return
    rows.append({
        "country_code": country_code,
        "country_name": country_name,
        "group_type": group_type,
        "group_code": group_code(group_name),
        "group_name": group_name,
        "is_member": "true",
        "source_id": "WIID",
        "valid_from": "",
        "valid_to": "",
        "notes": notes,
    })


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Arquivo não encontrado: {INPUT}")

    countries: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            country_code = clean(row.get("c3"))
            if not country_code:
                continue
            countries[country_code]["country_name"].append(clean(row.get("country")))
            for field in ("region_un", "region_un_sub", "region_wb", "incomegroup", "eu", "oecd"):
                countries[country_code][field].append(clean(row.get(field)))

    output_rows: list[dict[str, str]] = []
    for country_code, values in sorted(countries.items()):
        country_name = most_common(values["country_name"])
        add_group(
            output_rows, country_code, country_name, "un_region",
            most_common(values["region_un"]),
            "Moda das observações da WIID; classificação geográfica.",
        )
        add_group(
            output_rows, country_code, country_name, "un_subregion",
            most_common(values["region_un_sub"]),
            "Moda das observações da WIID; classificação geográfica.",
        )
        add_group(
            output_rows, country_code, country_name, "world_bank_region",
            most_common(values["region_wb"]),
            "Moda das observações da WIID; classificação regional.",
        )
        add_group(
            output_rows, country_code, country_name, "income_group",
            most_common(values["incomegroup"]),
            "Moda das observações da WIID; grupo de renda.",
        )

        if most_common(values["eu"]).upper() == "EU":
            add_group(
                output_rows, country_code, country_name, "integration",
                "European Union", "Marcador disponível na WIID.",
            )
        if most_common(values["oecd"]).upper() == "OECD":
            add_group(
                output_rows, country_code, country_name, "integration",
                "OECD", "Marcador disponível na WIID.",
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "country_code", "country_name", "group_type", "group_code", "group_name",
        "is_member", "source_id", "valid_from", "valid_to", "notes",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Grupos de comparação gravados: {OUTPUT} ({len(output_rows)} linhas)")


if __name__ == "__main__":
    main()
