from __future__ import annotations

import argparse
import csv
import io
import os
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILE = ROOT / "sql" / "001_schema_aiven.sql"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"


def clean(value: str | None, *, empty: str | None = None) -> str | None:
    if value is None:
        return empty
    value = value.strip()
    if value == "" or value.lower() in {"nan", "nat", "none", "null"}:
        return empty
    return value


def boolean_or_none(value: str | None) -> str | None:
    value = clean(value)
    if value is None:
        return None
    if value.lower() in {"true", "1", "yes"}:
        return "true"
    if value.lower() in {"false", "0", "no"}:
        return "false"
    raise ValueError(f"Booleano não reconhecido: {value}")


def numeric_or_none(value: str | None) -> str | None:
    return clean(value)


def row_panel(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("country_code")) or clean(row.get("country_text_id")),
        clean(row.get("country_name")),
        clean(row.get("year")),
        clean(row.get("historical_date")),
        *[numeric_or_none(row.get(name)) for name in (
            "v2x_polyarchy", "v2x_libdem", "v2x_partipdem", "v2x_delibdem",
            "v2x_egaldem", "v2x_freexp_altinf", "v2x_frassoc_thick",
            "v2x_suffr", "v2x_elecoff", "v2x_gender", "v2xeg_eqdr",
            "v2xeg_eqprotec", "v2xeg_eqaccess", "gini_mean_available_records",
            "gini_min", "gini_max", "gini_records",
        )],
        clean(row.get("source")),
    ]


def row_wid(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("country")),
        clean(row.get("variable")),
        clean(row.get("percentile")),
        clean(row.get("year")),
        numeric_or_none(row.get("value")),
        clean(row.get("age")),
        clean(row.get("pop")),
        clean(row.get("data_quality")),
        "WID",
    ]


def row_wealth(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("country")),
        clean(row.get("year")),
        clean(row.get("indicator")),
        clean(row.get("population_group")),
        numeric_or_none(row.get("share_percent")),
        "WID",
    ]


def row_wiid(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("id")), clean(row.get("c3")), clean(row.get("country")),
        clean(row.get("year")), numeric_or_none(row.get("gini")),
        numeric_or_none(row.get("mean_usd")), numeric_or_none(row.get("median_usd")),
        numeric_or_none(row.get("top5")), numeric_or_none(row.get("top10")),
        numeric_or_none(row.get("bottom40")), numeric_or_none(row.get("ratio_top20bottom20")),
        clean(row.get("quality")), numeric_or_none(row.get("quality_score")),
        clean(row.get("resource")), clean(row.get("scale")), clean(row.get("sharing_unit")),
        clean(row.get("survey")), "WIID",
    ]


def row_gap(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("country")), clean(row.get("year")),
        numeric_or_none(row.get("female_mean_ppp2021")),
        numeric_or_none(row.get("male_mean_ppp2021")),
        numeric_or_none(row.get("female_to_male_ratio")),
        numeric_or_none(row.get("gender_pay_gap_percent")), "ILOSTAT",
    ]


def row_modelled(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("country")), clean(row.get("year")),
        numeric_or_none(row.get("value")), clean(row.get("indicator")),
        clean(row.get("source")), "ILOSTAT",
    ]


def row_pnad(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("year")), clean(row.get("quarter")), clean(row.get("period")),
        clean(row.get("aggregation_level")), clean(row.get("sex")), clean(row.get("race")),
        numeric_or_none(row.get("mean_monthly_work_income_nominal")),
        numeric_or_none(row.get("weighted_population")), clean(row.get("sample_n")),
        clean(row.get("income_variable")), clean(row.get("weight_variable")),
        boolean_or_none(row.get("deflator_applied")) or "false",
    ]


def row_findex(row: dict[str, str]) -> list[str | None]:
    source_names = [
        "account.t.d", "borrow.any.t.d", "save.any.t.d", "fin4.d",
        "fin17a.17a1.d", "fin17a", "fin17b", "fin17c", "fin22d", "fin22e",
        "fin31a.31b", "fin40a", "fin41", "fin35", "dig.acc",
    ]
    return [
        clean(row.get("codewb")), clean(row.get("countrynewwb")), clean(row.get("year")),
        clean(row.get("group")), clean(row.get("group2"), empty=""),
        *[numeric_or_none(row.get(name)) for name in source_names],
        "GLOBAL_FINDEX",
    ]


def row_coverage(row: dict[str, str]) -> list[str | None]:
    return [
        clean(row.get("fonte")), clean(row.get("dimensao")),
        clean(row.get("categoria")), clean(row.get("observacoes")),
    ]


class LoadSpec:
    def __init__(
        self,
        table: str,
        path: Path,
        columns: list[str],
        transform: Callable[[dict[str, str]], list[str | None]],
    ) -> None:
        self.table = table
        self.path = path
        self.columns = columns
        self.transform = transform


SPECS = [
    LoadSpec(
        "country_year_panel",
        PROCESSED / "painel_analitico_pais_ano.csv",
        [
            "country_code", "country_name", "year", "historical_date",
            "v2x_polyarchy", "v2x_libdem", "v2x_partipdem", "v2x_delibdem",
            "v2x_egaldem", "v2x_freexp_altinf", "v2x_frassoc_thick", "v2x_suffr",
            "v2x_elecoff", "v2x_gender", "v2xeg_eqdr", "v2xeg_eqprotec",
            "v2xeg_eqaccess", "gini_mean", "gini_min", "gini_max", "gini_records",
            "inequality_source",
        ],
        row_panel,
    ),
    LoadSpec(
        "wid_income_distribution",
        PROCESSED / "wid_selecao_2002_2026.csv",
        ["country_code", "variable_code", "percentile", "year", "value", "age_code", "population_group", "data_quality", "source_id"],
        row_wid,
    ),
    LoadSpec(
        "wid_wealth_concentration",
        TABLES / "wid_brasil_concentracao.csv",
        ["country_code", "year", "indicator_code", "population_group", "share_percent", "source_id"],
        row_wealth,
    ),
    LoadSpec(
        "wiid_inequality",
        PROCESSED / "wiid_2002_2026.csv",
        ["observation_id", "country_code", "country_name", "year", "gini", "mean_usd", "median_usd", "top_5_share", "top_10_share", "bottom_40_share", "top20_bottom20_ratio", "quality_label", "quality_score", "resource", "scale", "sharing_unit", "survey", "source_id"],
        row_wiid,
    ),
    LoadSpec(
        "labor_gender_gap",
        TABLES / "ilostat_gap_genero.csv",
        ["country_name", "year", "female_mean_ppp2021", "male_mean_ppp2021", "female_to_male_ratio", "gender_pay_gap_percent", "source_id"],
        row_gap,
    ),
    LoadSpec(
        "labor_gender_modelled",
        PROCESSED / "ilostat_gender_income_gap_modelado.csv",
        ["country_name", "year", "value", "indicator_label", "source_label", "source_id"],
        row_modelled,
    ),
    LoadSpec(
        "brazil_pnad_group_income",
        PROCESSED / "pnad_rendimento_sexo_raca.csv",
        ["year", "quarter", "period", "aggregation_level", "sex", "race", "mean_monthly_work_income_nominal", "weighted_population", "sample_n", "income_variable", "weight_variable", "deflator_applied"],
        row_pnad,
    ),
    LoadSpec(
        "financial_inclusion_waves",
        PROCESSED / "global_findex_selecionado.csv",
        ["country_code", "country_name", "year", "group_name", "group_detail", "account_share", "borrow_any_share", "save_any_share", "fin4_share", "fin17a_17a1_share", "fin17a_share", "fin17b_share", "fin17c_share", "fin22d_share", "fin22e_share", "fin31a_31b_share", "fin40a_share", "fin41_share", "fin35_share", "digital_account_share", "source_id"],
        row_findex,
    ),
    LoadSpec(
        "country_group_membership",
        PROCESSED / "country_group_membership.csv",
        ["country_code", "country_name", "group_type", "group_code", "group_name", "is_member", "source_id", "valid_from", "valid_to", "notes"],
        lambda row: [
            clean(row.get("country_code")), clean(row.get("country_name")), clean(row.get("group_type")),
            clean(row.get("group_code")), clean(row.get("group_name")), boolean_or_none(row.get("is_member")) or "true",
            clean(row.get("source_id")), clean(row.get("valid_from")), clean(row.get("valid_to")), clean(row.get("notes")),
        ],
    ),
    LoadSpec(
        "source_coverage",
        TABLES / "cobertura_processada.csv",
        ["source_id", "dimension_name", "category", "observations"],
        row_coverage,
    ),
]


def sql_identifiers(table: str, columns: Iterable[str]):
    from psycopg import sql

    return sql.SQL("{}.{} ({})").format(
        sql.Identifier("analytics"),
        sql.Identifier(table),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )


def write_copy_rows(copy, rows: Iterable[list[str | None]]) -> int:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    count = 0
    for row in rows:
        writer.writerow(["" if value is None else value for value in row])
        copy.write(buffer.getvalue())
        buffer.seek(0)
        buffer.truncate(0)
        count += 1
    return count


def load_spec(conn, spec: LoadSpec) -> int:
    from psycopg import sql

    with spec.path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        copy_sql = sql.SQL("COPY {} FROM STDIN WITH (FORMAT CSV, NULL '')").format(
            sql_identifiers(spec.table, spec.columns)
        )
        with conn.cursor() as cur, cur.copy(copy_sql) as copy:
            return write_copy_rows(copy, (spec.transform(row) for row in reader))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Carrega as tabelas analíticas na Aiven.")
    parser.add_argument("--database-url", default=os.getenv("AIVEN_DATABASE_URL"))
    parser.add_argument("--schema-file", type=Path, default=SCHEMA_FILE)
    parser.add_argument("--replace", action="store_true", help="limpa as tabelas analíticas antes da carga")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.database_url:
        raise SystemExit("AIVEN_DATABASE_URL não foi definida.")

    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("Instale as dependências com: pip install -r requirements-aiven.txt") from exc

    schema_sql = args.schema_file.read_text(encoding="utf-8")
    with psycopg.connect(args.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            if args.replace:
                table_names = ", ".join(
                    f"analytics.{spec.table}" for spec in SPECS
                )
                cur.execute(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        conn.commit()

        for spec in SPECS:
            if not spec.path.exists():
                print(f"Arquivo não encontrado: {spec.path}")
                continue
            count = load_spec(conn, spec)
            conn.commit()
            print(f"{spec.table}: {count} linhas")

        with conn.cursor() as cur:
            cur.execute("SET search_path TO analytics, public")
            cur.execute("ANALYZE")
        conn.commit()
    print("Carga concluída.")


if __name__ == "__main__":
    main()
