from __future__ import annotations

import csv
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.utils import ensure_project_dirs, find_outer_entry, load_config, project_path, source_zip, write_csv


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def shared_strings(book: zipfile.ZipFile) -> list[str]:
    try:
        stream = book.open("xl/sharedStrings.xml")
    except KeyError:
        return []
    values: list[str] = []
    for _event, element in ET.iterparse(stream, events=("end",)):
        if local(element.tag) == "si":
            values.append("".join(node.text or "" for node in element.iter() if local(node.tag) == "t"))
            element.clear()
    stream.close()
    return values


def column_number(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference.upper())
    if not letters:
        return 0
    value = 0
    for char in letters.group(0):
        value = value * 26 + ord(char) - 64
    return value - 1


def rows_from_sheet(book: zipfile.ZipFile, sheet_name: str, strings: list[str]):
    stream = book.open(sheet_name)
    for _event, element in ET.iterparse(stream, events=("end",)):
        if local(element.tag) != "row":
            continue
        values: dict[int, str] = {}
        for cell in list(element):
            if local(cell.tag) != "c":
                continue
            ref = cell.attrib.get("r", "")
            value_node = next((node for node in list(cell) if local(node.tag) == "v"), None)
            value = value_node.text if value_node is not None and value_node.text is not None else ""
            if cell.attrib.get("t") == "s" and value.isdigit() and int(value) < len(strings):
                value = strings[int(value)]
            values[column_number(ref)] = value
        yield values
        element.clear()
    stream.close()


def row_values(row: dict[int, str], headers: list[str]) -> dict[str, str]:
    return {header: row.get(index, "") for index, header in enumerate(headers)}


def process_wiid(outer: zipfile.ZipFile, config: dict) -> int:
    entry = find_outer_entry(outer, "WIID-08SEP2026.xlsx")
    if entry is None:
        raise FileNotFoundError("WIID-08SEP2026.xlsx não encontrado.")
    output = project_path(config, "processed") / "wiid_2002_2026.csv"
    count = 0
    with outer.open(entry) as raw_xlsx:
        with zipfile.ZipFile(raw_xlsx) as book:
            strings = shared_strings(book)
            rows = rows_from_sheet(book, "xl/worksheets/sheet1.xml", strings)
            headers = next(rows)
            header_list = [headers[index] for index in range(max(headers) + 1)]
            with output.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=header_list, extrasaction="ignore")
                writer.writeheader()
                for row in rows:
                    item = row_values(row, header_list)
                    try:
                        year = int(float(item.get("year", "")))
                    except ValueError:
                        continue
                    if 2002 <= year <= 2026:
                        writer.writerow(item)
                        count += 1
    return count


def process_findex(outer: zipfile.ZipFile, config: dict) -> int:
    entry = find_outer_entry(outer, "GlobalFindexDatabase2025.xlsx")
    if entry is None:
        raise FileNotFoundError("GlobalFindexDatabase2025.xlsx não encontrado.")
    output = project_path(config, "processed") / "global_findex_selecionado.csv"
    target_years = {int(value) for value in config["sources"].get("findex_years", [2011, 2014, 2017, 2021, 2024])}
    preferred = [
        "countrynewwb", "codewb", "year", "group", "group2",
        "account.t.d", "borrow.any.t.d", "save.any.t.d", "fin4.d",
        "fin17a.17a1.d", "fin17a", "fin17b", "fin17c", "fin22d", "fin22e",
        "fin31a.31b", "fin40a", "fin41", "fin35", "dig.acc",
    ]
    count = 0
    with outer.open(entry) as raw_xlsx:
        with zipfile.ZipFile(raw_xlsx) as book:
            strings = shared_strings(book)
            rows = rows_from_sheet(book, "xl/worksheets/sheet2.xml", strings)
            first = next(rows)
            headers = [first[index] for index in range(max(first) + 1)]
            selected = [header for header in preferred if header in headers]
            if not selected:
                raise ValueError("Não foi possível localizar as colunas principais do Global Findex.")
            with output.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=selected, extrasaction="ignore")
                writer.writeheader()
                for row in rows:
                    item = row_values(row, headers)
                    try:
                        year = int(float(item.get("year", "")))
                    except ValueError:
                        continue
                    if year in target_years:
                        writer.writerow({key: item.get(key, "") for key in selected})
                        count += 1
    return count


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    with zipfile.ZipFile(source_zip(config)) as outer:
        wiid_count = process_wiid(outer, config)
        findex_count = process_findex(outer, config)
    print(f"WIID filtrado: {wiid_count} linhas")
    print(f"Global Findex filtrado: {findex_count} linhas")


if __name__ == "__main__":
    main()
