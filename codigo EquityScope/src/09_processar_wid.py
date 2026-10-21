from __future__ import annotations

import csv
import io
import zipfile

from src.utils import ensure_project_dirs, find_outer_entry, load_config, project_path, project_period, source_zip


DATA_FIELDS = ["country", "variable", "percentile", "year", "value", "age", "pop", "data_quality"]


def main() -> None:
    config = load_config()
    ensure_project_dirs(config)
    start, end = project_period(config)
    codes = [str(code).upper() for code in config["sources"].get("wid_country_codes", ["BR"])]
    output = project_path(config, "processed") / f"wid_selecao_{start}_{end}.csv"
    metadata_output = project_path(config, "metadata") / "wid_metadata_selecionado.csv"
    row_count = 0
    metadata_count = 0

    with zipfile.ZipFile(source_zip(config)) as outer:
        outer_entry = find_outer_entry(outer, "wid_all_data.zip")
        if outer_entry is None:
            raise FileNotFoundError("wid_all_data.zip não encontrado no ZIP bruto.")
        with outer.open(outer_entry) as nested_stream:
            with zipfile.ZipFile(nested_stream) as nested:
                with output.open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=DATA_FIELDS)
                    writer.writeheader()
                    for code in codes:
                        entry_name = f"WID_data_{code}.csv"
                        try:
                            info = nested.getinfo(entry_name)
                        except KeyError:
                            print(f"WID: país não encontrado: {code}")
                            continue
                        with nested.open(info) as raw:
                            text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
                            for row in csv.DictReader(text, delimiter=";"):
                                try:
                                    year = int(row.get("year", ""))
                                except ValueError:
                                    continue
                                if start <= year <= end:
                                    writer.writerow({field: row.get(field, "") for field in DATA_FIELDS})
                                    row_count += 1

                with metadata_output.open("w", encoding="utf-8-sig", newline="") as handle:
                    metadata_fields: list[str] | None = None
                    writer = None
                    for code in codes:
                        entry_name = f"WID_metadata_{code}.csv"
                        try:
                            info = nested.getinfo(entry_name)
                        except KeyError:
                            continue
                        with nested.open(info) as raw:
                            text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
                            reader = csv.DictReader(text, delimiter=";")
                            if metadata_fields is None:
                                metadata_fields = list(reader.fieldnames or [])
                                writer = csv.DictWriter(handle, fieldnames=metadata_fields)
                                writer.writeheader()
                            for row in reader:
                                if writer is not None:
                                    writer.writerow(row)
                                    metadata_count += 1

    print(f"WID selecionado: {row_count} linhas -> {output}")
    print(f"Metadados WID: {metadata_count} linhas -> {metadata_output}")


if __name__ == "__main__":
    main()
