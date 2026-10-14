from __future__ import annotations

import csv
import io
import zipfile

from src.utils import ensure_project_dirs, load_config, project_path, project_period, source_zip, write_csv


def stream_csv_rows(archive: zipfile.ZipFile, info: zipfile.ZipInfo):
    with archive.open(info) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
        yield from csv.DictReader(text)


def clean_earnings(archive: zipfile.ZipFile, start: int, end: int):
    for info in archive.infolist():
        if "ILOSTAT" not in info.filename or "EAR_EMTA" not in info.filename:
            continue
        for row in stream_csv_rows(archive, info):
            try:
                year = int(row.get("time", ""))
            except ValueError:
                continue
            if start <= year <= end:
                yield {
                    "country": row.get("ref_area.label", ""),
                    "year": year,
                    "sex": row.get("sex.label", ""),
                    "currency": row.get("classif1.label", ""),
                    "value": row.get("obs_value", ""),
                    "source": row.get("source.label", ""),
                    "indicator": row.get("indicator.label", ""),
                    "note_indicator": row.get("note_indicator.label", ""),
                    "note_source": row.get("note_source.label", ""),
                }


def clean_modeled_gap(archive: zipfile.ZipFile, start: int, end: int):
    for info in archive.infolist():
        if "ILOSTAT" not in info.filename or "LAP_2FTM" not in info.filename:
            continue
        for row in stream_csv_rows(archive, info):
            try:
                year = int(row.get("time", ""))
            except ValueError:
                continue
            if start <= year <= end:
                yield {
                    "country": row.get("ref_area.label", ""),
                    "year": year,
                    "value": row.get("obs_value", ""),
                    "source": row.get("source.label", ""),
                    "indicator": row.get("indicator.label", ""),
                }


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    start, end = project_period(config)
    with zipfile.ZipFile(source_zip(config)) as archive:
        earnings = list(clean_earnings(archive, start, end))
        gaps = list(clean_modeled_gap(archive, start, end))

    processed = project_path(config, "processed")
    earnings_path = processed / "ilostat_remuneracao_por_sexo.csv"
    gap_path = processed / "ilostat_gender_income_gap_modelado.csv"
    write_csv(earnings_path, list(earnings[0]) if earnings else ["country"], earnings)
    write_csv(gap_path, list(gaps[0]) if gaps else ["country"], gaps)
    print(f"ILOSTAT remuneração: {len(earnings)} linhas -> {earnings_path}")
    print(f"ILOSTAT modelado: {len(gaps)} linhas -> {gap_path}")


if __name__ == "__main__":
    main()
