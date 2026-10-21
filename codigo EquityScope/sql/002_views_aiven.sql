SET search_path TO analytics, public;

CREATE OR REPLACE VIEW v_pnad_latest_by_group AS
SELECT DISTINCT ON (aggregation_level, sex, race)
    year,
    quarter,
    period,
    aggregation_level,
    sex,
    race,
    mean_monthly_work_income_nominal,
    weighted_population,
    sample_n,
    deflator_applied
FROM brazil_pnad_group_income
ORDER BY aggregation_level, sex, race, year DESC, quarter DESC;

CREATE OR REPLACE VIEW v_country_year_context AS
SELECT
    country_code,
    country_name,
    year,
    gini_mean,
    gini_min,
    gini_max,
    gini_records,
    v2x_polyarchy,
    v2x_libdem,
    v2x_partipdem,
    v2x_delibdem,
    v2x_egaldem,
    v2x_gender,
    v2xeg_eqdr,
    v2xeg_eqprotec,
    v2xeg_eqaccess,
    inequality_source
FROM country_year_panel;

CREATE OR REPLACE VIEW v_country_comparison_context AS
SELECT
    p.country_code,
    p.country_name,
    p.year,
    p.gini_mean,
    p.gini_min,
    p.gini_max,
    p.gini_records,
    p.v2x_gender,
    p.v2xeg_eqdr,
    p.v2xeg_eqprotec,
    p.v2xeg_eqaccess,
    g.group_type,
    g.group_code,
    g.group_name,
    g.source_id AS group_source_id
FROM country_year_panel AS p
LEFT JOIN country_group_membership AS g
    ON g.country_code = p.country_code;

CREATE OR REPLACE VIEW v_storage_usage AS
SELECT
    current_database() AS database_name,
    pg_database_size(current_database()) AS database_bytes,
    pg_size_pretty(pg_database_size(current_database())) AS database_size,
    current_setting('block_size')::integer AS block_size_bytes;
