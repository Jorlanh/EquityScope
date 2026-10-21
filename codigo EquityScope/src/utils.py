from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | Path = ROOT / "config.yaml") -> dict[str, Any]:
    """Lê config.yaml, escrito em sintaxe JSON válida para não exigir PyYAML."""
    config_path = Path(path)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    text = config_path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Instale PyYAML para ler este arquivo YAML.") from exc
        return yaml.safe_load(text)


def source_zip(config: dict[str, Any]) -> Path:
    path = Path(config["sources"]["source_zip"]).expanduser()
    return path if path.is_absolute() else ROOT / path


def project_period(config: dict[str, Any]) -> tuple[int, int]:
    project = config["project"]
    return int(project["period_start"]), int(project["period_end"])


def project_path(config: dict[str, Any], key: str) -> Path:
    value = Path(config["paths"][key])
    return value if value.is_absolute() else ROOT / value


def ensure_project_dirs(config: dict[str, Any]) -> None:
    for key in config.get("paths", {}):
        project_path(config, key).mkdir(parents=True, exist_ok=True)


def normalize_label(value: str | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.casefold()
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def parse_year(value: str | None) -> int | None:
    if value is None:
        return None
    pnad = re.search(r"PNADC_\d{2}(20\d{2})", str(value), flags=re.IGNORECASE)
    if pnad:
        return int(pnad.group(1))
    match = re.search(r"(?<!\d)(19|20)\d{2}(?!\d)", str(value))
    return int(match.group(0)) if match else None


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def find_outer_entry(zip_file: Any, suffix: str) -> Any | None:
    suffix = suffix.casefold()
    for info in zip_file.infolist():
        if info.filename.casefold().endswith(suffix):
            return info
    return None
