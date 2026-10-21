from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "outputs" / "tables"

WID_CODE = {"BRA": "BR", "USA": "US", "CHN": "CN"}
FINDEX_LABELS = {
    "account_share": "Conta financeira",
    "borrow_any_share": "Tomou empréstimo",
    "save_any_share": "Poupou",
    "digital_account_share": "Conta digital",
    "fin40a_share": "Cartão de crédito",
    "fin41_share": "Cartão de débito",
}


def csv_file(name: str, **kwargs) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


@st.cache_data(show_spinner=False)
def load_local() -> dict[str, pd.DataFrame]:
    panel = csv_file("painel_analitico_pais_ano.csv")
    if "country_code" in panel:
        panel["country_code"] = panel["country_code"].fillna(panel.get("country_text_id"))
    findex = csv_file("global_findex_selecionado.csv")
    findex = findex.rename(columns={
        "countrynewwb": "country_name",
        "codewb": "country_code",
        "account.t.d": "account_share",
        "borrow.any.t.d": "borrow_any_share",
        "save.any.t.d": "save_any_share",
        "fin4.d": "fin4_share",
        "fin40a": "fin40a_share",
        "fin41": "fin41_share",
        "dig.acc": "digital_account_share",
    })
    wiid = csv_file("wiid_2002_2026.csv").rename(columns={
        "c3": "country_code",
        "country": "country_name",
    })

    return {
        "panel": panel,
        "groups": csv_file("country_group_membership.csv"),
        "wiid": wiid,
        "wid": csv_file("wid_selecao_2002_2026.csv"),
        "pnad": csv_file("pnad_rendimento_sexo_raca.csv"),
        "labor": (
            pd.read_csv(TABLES / "ilostat_gap_genero.csv").rename(columns={"country": "country_name"})
            if (TABLES / "ilostat_gap_genero.csv").exists()
            else pd.DataFrame()
        ),
        "findex": findex,
    }


def fetch_table(conn, query: str) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [column.name for column in cur.description]
    return pd.DataFrame(rows, columns=columns)


def load_aiven(url: str) -> dict[str, pd.DataFrame]:
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Instale requirements-frontend.txt para consultar a Aiven.") from exc

    queries = {
        "panel": """
            SELECT country_code, country_name, year, gini_mean, gini_min,
                   gini_max, gini_records, v2x_gender, v2xeg_eqdr,
                   v2xeg_eqprotec, v2xeg_eqaccess
            FROM analytics.country_year_panel
        """,
        "groups": """
            SELECT country_code, country_name, group_type, group_code,
                   group_name, is_member
            FROM analytics.country_group_membership
        """,
        "wiid": """
            SELECT country_code, country_name, year, gini, mean_usd,
                   median_usd, top_5_share, top_10_share, bottom_40_share
            FROM analytics.wiid_inequality
        """,
        "wid": """
            SELECT country_code AS country, variable_code AS variable,
                   percentile, year, value, age_code AS age,
                   population_group AS pop, data_quality
            FROM analytics.wid_income_distribution
        """,
        "pnad": """
            SELECT year, quarter, period, aggregation_level, sex, race,
                   mean_monthly_work_income_nominal,
                   weighted_population, sample_n, deflator_applied
            FROM analytics.brazil_pnad_group_income
        """,
        "labor": """
            SELECT country_name, year, female_mean_ppp2021,
                   male_mean_ppp2021, female_to_male_ratio,
                   gender_pay_gap_percent
            FROM analytics.labor_gender_gap
        """,
        "findex": """
            SELECT country_code, country_name, year, group_name AS group,
                   group_detail AS group2, account_share,
                   borrow_any_share, save_any_share, digital_account_share,
                   fin40a_share, fin41_share
            FROM analytics.financial_inclusion_waves
        """,
    }

    with psycopg.connect(url) as conn:
        return {name: fetch_table(conn, query) for name, query in queries.items()}


def load_data(source: str, url: str) -> tuple[dict[str, pd.DataFrame], str]:
    if source == "Aiven":
        try:
            return load_aiven(url), "Aiven"
        except Exception as exc:  # a mensagem aparece no painel, sem derrubar a aplicação
            st.warning(f"Não foi possível consultar a Aiven: {exc}. Exibindo os arquivos locais.")
    return load_local(), "Arquivos locais"


def to_number(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    frame = frame.copy()
    for column in columns:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def country_lists(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, list[str]]:
    groups = data["groups"]
    if not groups.empty:
        lookup = groups[["country_code", "country_name"]].drop_duplicates()
    else:
        lookup = data["panel"][["country_code", "country_name"]].drop_duplicates()
    lookup = lookup.dropna().sort_values("country_name")
    return lookup, lookup["country_code"].tolist()


def filter_countries(frame: pd.DataFrame, selected: list[str], column: str = "country_code") -> pd.DataFrame:
    if not selected or column not in frame:
        return frame
    return frame[frame[column].isin(selected)].copy()


def select_filters(data: dict[str, pd.DataFrame]) -> tuple[list[str], tuple[int, int], pd.DataFrame]:
    groups = data["groups"]
    lookup, country_codes = country_lists(data)
    country_labels = dict(zip(lookup["country_code"], lookup["country_name"]))

    st.sidebar.subheader("Filtros")
    group_type = "Todos"
    group_name = "Todos"
    if not groups.empty:
        types = ["Todos"] + sorted(groups["group_type"].dropna().unique().tolist())
        group_type = st.sidebar.selectbox("Tipo de agrupamento", types)
        available = groups if group_type == "Todos" else groups[groups["group_type"] == group_type]
        names = ["Todos"] + sorted(available["group_name"].dropna().unique().tolist())
        group_name = st.sidebar.selectbox("Grupo", names)
        if group_name != "Todos":
            available = available[available["group_name"] == group_name]
        group_codes = set(available["country_code"])
        country_codes = [code for code in country_codes if code in group_codes]

    defaults = [code for code in ("BRA", "USA", "CHN") if code in country_codes]
    selected = st.sidebar.multiselect(
        "Países",
        country_codes,
        default=defaults or country_codes[:3],
        format_func=lambda code: country_labels.get(code, code),
    )

    panel = to_number(data["panel"], ["year"])
    min_year = int(panel["year"].min()) if not panel.empty else 2002
    max_year = int(panel["year"].max()) if not panel.empty else 2026
    years = st.sidebar.slider("Período", min_year, max_year, (min_year, max_year))
    return selected, years, lookup


def chart_line(
    frame: pd.DataFrame,
    x: str,
    y: str,
    color: str,
    title: str,
    y_title: str,
    lower: str | None = None,
    upper: str | None = None,
    details: list[str] | None = None,
    key: str = "chart",
):
    if frame.empty or y not in frame:
        st.info("Não há dados para os filtros escolhidos.")
        return
    frame = frame.sort_values([color, x] if color in frame else [x]).copy()
    hover_data: dict[str, object] = {x: False, y: ":.2f"}
    for column in details or []:
        if column in frame and column not in (x, y, color):
            hover_data[column] = ":.2f" if pd.api.types.is_numeric_dtype(frame[column]) else True
    if lower and lower in frame:
        hover_data[lower] = ":.2f"
    if upper and upper in frame:
        hover_data[upper] = ":.2f"
    labels = {x: "Ano", y: y_title, color: "Série"}
    labels.update({column: column.replace("_", " ").capitalize() for column in (details or [])})
    if lower:
        labels[lower] = "Mínimo"
    if upper:
        labels[upper] = "Máximo"
    fig = px.line(
        frame,
        x=x,
        y=y,
        color=color,
        markers=True,
        title=title,
        hover_data=hover_data,
        labels=labels,
    )
    fig.update_layout(
        yaxis_title=y_title,
        xaxis_title="Ano",
        legend_title_text="Clique na legenda para ocultar ou exibir séries",
        hovermode="x unified",
        uirevision=key,
        margin={"t": 65, "r": 20, "b": 55, "l": 60},
    )
    fig.update_traces(
        selector={"mode": "lines+markers"},
        marker={"size": 7},
    )
    config = {
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    }
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        config=config,
        key=key,
        on_select="rerun",
        selection_mode=("points",),
    )
    try:
        points = event.selection.points
    except AttributeError:
        try:
            points = event["selection"]["points"]
        except (KeyError, TypeError):
            points = []
    if points:
        point = points[0]
        value = point.get("y")
        year = point.get("x")
        series = point.get("fullData", {}).get("name") if isinstance(point.get("fullData"), dict) else None
        if not series and point.get("curve_number") is not None:
            try:
                series = fig.data[int(point["curve_number"])].name
            except (IndexError, TypeError, ValueError):
                series = None
        try:
            value_text = f"{value:.2f}"
        except (TypeError, ValueError):
            value_text = str(value)
        selected_rows = frame.copy()
        if year is not None and x in selected_rows:
            selected_rows = selected_rows[selected_rows[x].astype(str) == str(year)]
        if series and color in selected_rows:
            selected_rows = selected_rows[selected_rows[color].astype(str) == str(series)]
        if not selected_rows.empty and value is not None and y in selected_rows:
            numeric_y = pd.to_numeric(selected_rows[y], errors="coerce")
            if numeric_y.notna().any():
                closest_index = (numeric_y - float(value)).abs().idxmin()
                selected_rows = selected_rows.loc[[closest_index]]
        extra = []
        if not selected_rows.empty:
            selected_row = selected_rows.iloc[0]
            if lower and upper and lower in selected_row and upper in selected_row:
                lower_value = pd.to_numeric(selected_row[lower], errors="coerce")
                upper_value = pd.to_numeric(selected_row[upper], errors="coerce")
                if pd.notna(lower_value) and pd.notna(upper_value):
                    extra.append(f"faixa: {lower_value:.2f}–{upper_value:.2f}")
            for column in details or []:
                if column in selected_row and pd.notna(selected_row[column]):
                    extra.append(f"{labels.get(column, column)}: {selected_row[column]}")
        suffix = f" ({'; '.join(extra)})" if extra else ""
        selected_text = f"Ponto selecionado: {series + ' · ' if series else ''}{year} — {y_title}: {value_text}{suffix}"
        st.caption(selected_text)
    else:
        st.caption("Passe o mouse para ver os valores. Clique em um ponto para fixar um detalhe; clique na legenda para comparar séries.")


def show_overview(data: dict[str, pd.DataFrame], selected: list[str], years: tuple[int, int], lookup: pd.DataFrame) -> None:
    panel = to_number(data["panel"], ["year", "gini_mean"])
    panel = panel[panel["year"].between(*years)]
    panel = filter_countries(panel, selected)

    countries = panel["country_code"].nunique() if not panel.empty else 0
    observations = len(panel)
    pnad = data["pnad"]
    findex = data["findex"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Países no painel", countries)
    c2.metric("Observações país-ano", observations)
    c3.metric("Linhas PNAD", len(pnad))
    c4.metric("Linhas Findex", len(findex))

    chart_line(
        panel.dropna(subset=["gini_mean"]),
        "year", "gini_mean", "country_name",
        "Desigualdade de renda no painel comparativo", "Gini médio disponível",
        lower="gini_min", upper="gini_max", details=["gini_records"], key="overview-gini",
    )
    st.caption("O gráfico usa os registros de Gini disponíveis na WIID para cada país e ano.")


def show_inequality(data: dict[str, pd.DataFrame], selected: list[str], years: tuple[int, int]) -> None:
    st.subheader("Renda e desigualdade")
    measure = st.radio("Indicador", ["Gini da WIID", "Série selecionada do WID"], horizontal=True)

    if measure == "Gini da WIID":
        frame = to_number(data["wiid"], ["year", "gini"])
        frame = frame[frame["year"].between(*years)]
        frame = filter_countries(frame, selected)
        if not frame.empty:
            frame = (
                frame.dropna(subset=["gini"])
                .groupby(["country_code", "country_name", "year"], as_index=False)
                .agg(
                    gini=("gini", "mean"),
                    gini_min=("gini", "min"),
                    gini_max=("gini", "max"),
                    gini_records=("gini", "size"),
                )
            )
        chart_line(
            frame,
            "year", "gini", "country_name", "Índice de Gini", "Gini",
            lower="gini_min", upper="gini_max", details=["gini_records"], key="wiid-gini",
        )
        st.dataframe(frame, use_container_width=True, hide_index=True)
        return

    frame = to_number(data["wid"], ["year", "value"])
    frame = frame[frame["year"].between(*years)]
    variables = sorted(frame["variable"].dropna().unique().tolist())
    variable = st.selectbox("Variável WID", variables) if variables else None
    if variable:
        frame = frame[frame["variable"] == variable]
    percentiles = sorted(frame["percentile"].dropna().unique().tolist())
    percentile = st.selectbox("Percentil", percentiles) if percentiles else None
    if percentile:
        frame = frame[frame["percentile"] == percentile]

    allowed = {WID_CODE.get(code, code) for code in selected}
    if allowed:
        frame = frame[frame["country"].isin(allowed)]
    chart_line(frame.dropna(subset=["value"]), "year", "value", "country", "Indicador selecionado do WID", "Valor", key="wid-series")
    st.dataframe(frame, use_container_width=True, hide_index=True)


def show_brazil(data: dict[str, pd.DataFrame], years: tuple[int, int]) -> None:
    st.subheader("Brasil: gênero, raça/cor e rendimento")
    st.warning("Os rendimentos da PNAD estão nominais. A comparação em valores reais depende da aplicação do deflator oficial.")
    frame = to_number(data["pnad"], ["year", "mean_monthly_work_income_nominal", "sample_n"])
    frame = frame[frame["year"].between(*years)]
    levels = sorted(frame["aggregation_level"].dropna().unique().tolist())
    level = st.selectbox("Nível de agregação", levels) if levels else None
    if level:
        frame = frame[frame["aggregation_level"] == level]
    sexes = sorted(frame["sex"].dropna().unique().tolist())
    races = sorted(frame["race"].dropna().unique().tolist())
    sex = st.multiselect("Sexo", sexes, default=sexes)
    race = st.multiselect("Raça/cor", races, default=races)
    if sex:
        frame = frame[frame["sex"].isin(sex)]
    if race:
        frame = frame[frame["race"].isin(race)]
    frame["grupo"] = frame["sex"].astype(str) + " / " + frame["race"].astype(str)
    chart_line(
        frame.dropna(subset=["mean_monthly_work_income_nominal"]),
        "period", "mean_monthly_work_income_nominal", "grupo",
        "Rendimento habitual mensal por grupo", "Rendimento nominal",
        details=["sample_n", "weighted_population", "deflator_applied"], key="pnad-income",
    )
    st.dataframe(frame, use_container_width=True, hide_index=True)


def show_labor_and_findex(data: dict[str, pd.DataFrame], selected: list[str], years: tuple[int, int], lookup: pd.DataFrame) -> None:
    left, right = st.columns(2)
    with left:
        st.subheader("Diferença de renda do trabalho")
        labor = to_number(data["labor"], ["year", "gender_pay_gap_percent"])
        labor = labor[labor["year"].between(*years)]
        selected_names = set(lookup[lookup["country_code"].isin(selected)]["country_name"])
        if selected_names:
            labor = labor[labor["country_name"].isin(selected_names)]
        chart_line(
            labor.dropna(subset=["gender_pay_gap_percent"]),
            "year", "gender_pay_gap_percent", "country_name",
            "Diferença de rendimento por gênero", "Diferença (%)",
            details=["female_mean_ppp2021", "male_mean_ppp2021", "female_to_male_ratio"], key="labor-gap",
        )

    with right:
        st.subheader("Inclusão financeira")
        findex = to_number(data["findex"], ["year"])
        findex = findex[findex["year"].between(*years)]
        findex = filter_countries(findex, selected)
        groups = sorted(findex["group"].dropna().unique().tolist())
        group = st.selectbox("Grupo do Findex", groups, index=groups.index("gender") if "gender" in groups else 0) if groups else None
        if group:
            findex = findex[findex["group"] == group]
        indicators = [column for column in FINDEX_LABELS if column in findex]
        indicator = st.selectbox("Indicador", indicators, format_func=lambda item: FINDEX_LABELS[item]) if indicators else None
        if indicator:
            chart_line(
                findex.dropna(subset=[indicator]),
                "year", indicator, "group2",
                FINDEX_LABELS[indicator], "Proporção", key="findex-indicator",
            )


def show_data(data: dict[str, pd.DataFrame], selected: list[str], years: tuple[int, int]) -> None:
    names = {
        "Painel país-ano": "panel",
        "WIID": "wiid",
        "WID": "wid",
        "PNAD": "pnad",
        "ILOSTAT": "labor",
        "Global Findex": "findex",
        "Grupos de comparação": "groups",
    }
    choice = st.selectbox("Tabela", list(names))
    frame = data[names[choice]].copy()
    if "year" in frame:
        frame = to_number(frame, ["year"])
        frame = frame[frame["year"].between(*years)]
    if "country_code" in frame:
        frame = filter_countries(frame, selected)
    st.write(f"{len(frame):,} linhas".replace(",", "."))
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button(
        "Baixar tabela filtrada",
        frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="equityscope_filtrado.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(page_title="EquityScope", page_icon="📊", layout="wide")
    st.title("EquityScope")
    st.caption("Desigualdade econômica, gênero, raça/cor e inclusão financeira")

    st.sidebar.header("Fonte dos dados")
    source = st.sidebar.radio("Usar", ["Arquivos processados", "Aiven"])
    aiven_url = st.sidebar.text_input(
        "URL do PostgreSQL",
        value=os.getenv("AIVEN_DATABASE_URL", ""),
        type="password",
        help="A URL não é salva pelo aplicativo.",
    )
    data, loaded_from = load_data("Aiven" if source == "Aiven" else "Local", aiven_url)
    st.sidebar.caption(f"Fonte atual: {loaded_from}")

    selected, years, lookup = select_filters(data)
    overview, inequality, brazil, labor, tables = st.tabs([
        "Visão geral", "Renda e desigualdade", "Brasil", "Trabalho e inclusão", "Dados",
    ])
    with overview:
        show_overview(data, selected, years, lookup)
    with inequality:
        show_inequality(data, selected, years)
    with brazil:
        show_brazil(data, years)
    with labor:
        show_labor_and_findex(data, selected, years, lookup)
    with tables:
        show_data(data, selected, years)


if __name__ == "__main__":
    main()
