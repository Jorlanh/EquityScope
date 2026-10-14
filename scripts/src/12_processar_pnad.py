from __future__ import annotations

import csv
import io
import re
import zipfile
from collections import defaultdict

from src.utils import ensure_project_dirs, load_config, project_path, source_zip, write_csv


SEX_LABELS = {"1": "homens", "2": "mulheres"}
RACE_LABELS = {
    "1": "branca",
    "2": "preta",
    "3": "amarela",
    "4": "parda",
    "5": "indigena",
    "9": "ignorada",
}


def field(line: bytes, start_one_based: int, width: int) -> str:
    start = start_one_based - 1
    return line[start:start + width].decode("latin1", errors="replace").strip()


def number(value: str) -> float | None:
    if not value or value in {".", "...", "nan", "NaN"}:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def update(aggregates: dict[tuple[str, str, str, str], list[float]], year: str, quarter: str, sex: str, race: str, income: float, weight: float) -> None:
    keys = [
        ("sexo_raca", sex, race),
        ("sexo", sex, "todos"),
        ("raca", "todos", race),
        ("total", "todos", "todos"),
    ]
    for level, group_sex, group_race in keys:
        key = (year, quarter, level, f"{group_sex}|{group_race}")
        current = aggregates.setdefault(key, [0.0, 0.0, 0.0])
        current[0] += income * weight
        current[1] += weight
        current[2] += 1


def process_microdata(nested: zipfile.ZipFile, filename: str, aggregates: dict) -> None:
    text_files = [name for name in nested.namelist() if name.lower().endswith(".txt")]
    if not text_files:
        print(f"PNAD sem TXT: {filename}", flush=True)
        return
    text_name = text_files[0]
    with nested.open(text_name) as raw:
        for line in raw:
            if not line.strip():
                continue
            year = field(line, 1, 4)
            quarter = field(line, 5, 1)
            sex = SEX_LABELS.get(field(line, 95, 1), "desconhecido")
            race = RACE_LABELS.get(field(line, 107, 1), "desconhecida")
            weight = number(field(line, 50, 15))
            income = number(field(line, 444, 8))
            if not year.isdigit() or weight is None or income is None or weight <= 0 or income < 0:
                continue
            update(aggregates, year, quarter, sex, race, income, weight)


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    output = project_path(config, "processed") / "pnad_rendimento_sexo_raca.csv"
    aggregates: dict[tuple[str, str, str, str], list[float]] = {}
    processed_files = 0

    with zipfile.ZipFile(source_zip(config)) as outer:
        infos = []
        for info in outer.infolist():
            name = info.filename.replace("\\", "/")
            if "PNAD Contínua" not in name or not re.search(r"PNADC_\d{2}20\d{2}[^/]*\.zip$", name, flags=re.IGNORECASE):
                continue
            infos.append(info)
        infos.sort(key=lambda info: info.filename)
        for info in infos:
            print(f"Processando {info.filename}", flush=True)
            with outer.open(info) as nested_stream:
                with zipfile.ZipFile(nested_stream) as nested:
                    process_microdata(nested, info.filename, aggregates)
            processed_files += 1

    rows = []
    for (year, quarter, level, groups), values in sorted(aggregates.items()):
        weighted_income, population_weight, sample_n = values
        if population_weight <= 0:
            continue
        group_sex, group_race = groups.split("|", 1)
        rows.append({
            "year": int(year),
            "quarter": int(quarter),
            "period": f"{year}-T{int(quarter)}",
            "aggregation_level": level,
            "sex": group_sex,
            "race": group_race,
            "mean_monthly_work_income_nominal": weighted_income / population_weight,
            "weighted_population": population_weight,
            "sample_n": int(sample_n),
            "income_variable": "VD4019 rendimento habitual de todos os trabalhos",
            "weight_variable": "V1028 peso com calibração",
            "deflator_applied": False,
        })

    fields = list(rows[0]) if rows else ["year"]
    write_csv(output, fields, rows)
    print(f"PNAD processada: {processed_files} arquivos, {len(rows)} agregações -> {output}")
    print("Rendimentos ainda estão nominais; aplique o deflator oficial antes de comparar valores reais.")


if __name__ == "__main__":
    main()
