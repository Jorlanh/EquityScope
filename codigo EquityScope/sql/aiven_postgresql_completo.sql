-- Armazena apenas extratos analíticos; os dados brutos permanecem fora do banco.

CREATE SCHEMA IF NOT EXISTS analytics;
SET search_path TO analytics, public;

CREATE TABLE IF NOT EXISTS source_catalog (
    source_id       text PRIMARY KEY,
    source_name     text NOT NULL,
    version_label   text,
    source_url      text,
    period_start    smallint,
    period_end      smallint,
    notes           text,
    loaded_at       timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS country_year_panel (
    country_code       char(3) NOT NULL,
    country_name       text NOT NULL,
    year               smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    historical_date    date,
    v2x_polyarchy      double precision,
    v2x_libdem         double precision,
    v2x_partipdem      double precision,
    v2x_delibdem       double precision,
    v2x_egaldem        double precision,
    v2x_freexp_altinf  double precision,
    v2x_frassoc_thick  double precision,
    v2x_suffr          double precision,
    v2x_elecoff        double precision,
    v2x_gender         double precision,
    v2xeg_eqdr         double precision,
    v2xeg_eqprotec     double precision,
    v2xeg_eqaccess     double precision,
    gini_mean          double precision,
    gini_min           double precision,
    gini_max           double precision,
    gini_records       integer,
    inequality_source  text,
    PRIMARY KEY (country_code, year)
);

CREATE TABLE IF NOT EXISTS wid_income_distribution (
    country_code       char(3) NOT NULL,
    variable_code      text NOT NULL,
    percentile         text NOT NULL,
    year               smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    value              double precision,
    age_code           smallint,
    population_group   text,
    data_quality       text,
    source_id          text NOT NULL DEFAULT 'WID',
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_wid_distribution_country_year
    ON wid_income_distribution (country_code, year);

CREATE TABLE IF NOT EXISTS wid_wealth_concentration (
    country_code       char(3) NOT NULL,
    year               smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    indicator_code     text NOT NULL,
    population_group   text NOT NULL,
    share_percent      double precision,
    source_id          text NOT NULL DEFAULT 'WID',
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_wid_wealth_country_year
    ON wid_wealth_concentration (country_code, year);

CREATE TABLE IF NOT EXISTS wiid_inequality (
    observation_id             bigint,
    country_code               char(3) NOT NULL,
    country_name               text,
    year                       smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    gini                       double precision,
    mean_usd                   double precision,
    median_usd                 double precision,
    top_5_share                double precision,
    top_10_share               double precision,
    bottom_40_share            double precision,
    top20_bottom20_ratio       double precision,
    quality_label              text,
    quality_score              double precision,
    resource                   text,
    scale                      text,
    sharing_unit               text,
    survey                     text,
    source_id                  text NOT NULL DEFAULT 'WIID',
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_wiid_country_year
    ON wiid_inequality (country_code, year);

CREATE TABLE IF NOT EXISTS labor_gender_gap (
    country_name               text NOT NULL,
    year                       smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    female_mean_ppp2021        double precision,
    male_mean_ppp2021          double precision,
    female_to_male_ratio       double precision,
    gender_pay_gap_percent     double precision,
    source_id                  text NOT NULL DEFAULT 'ILOSTAT',
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_labor_gap_country_year
    ON labor_gender_gap (country_name, year);

CREATE TABLE IF NOT EXISTS labor_gender_modelled (
    country_name               text NOT NULL,
    year                       smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    value                      double precision,
    indicator_label            text NOT NULL,
    source_label               text,
    source_id                  text NOT NULL DEFAULT 'ILOSTAT',
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_labor_modelled_country_year
    ON labor_gender_modelled (country_name, year);

CREATE TABLE IF NOT EXISTS brazil_pnad_group_income (
    year                              smallint NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    quarter                           smallint NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    period                            text NOT NULL,
    aggregation_level                text NOT NULL,
    sex                               text NOT NULL,
    race                              text NOT NULL,
    mean_monthly_work_income_nominal numeric(18, 2),
    weighted_population              numeric(20, 2),
    sample_n                          integer,
    income_variable                  text,
    weight_variable                  text,
    deflator_applied                 boolean NOT NULL DEFAULT false,
    PRIMARY KEY (year, quarter, aggregation_level, sex, race)
);

CREATE INDEX IF NOT EXISTS ix_pnad_group_income_period
    ON brazil_pnad_group_income (year, quarter, sex, race);

CREATE TABLE IF NOT EXISTS financial_inclusion_waves (
    country_code             char(3) NOT NULL,
    country_name             text NOT NULL,
    year                     smallint NOT NULL CHECK (year IN (2011, 2014, 2017, 2021, 2024)),
    group_name               text NOT NULL,
    group_detail             text NOT NULL DEFAULT '',
    account_share            double precision,
    borrow_any_share         double precision,
    save_any_share           double precision,
    fin4_share               double precision,
    fin17a_17a1_share        double precision,
    fin17a_share             double precision,
    fin17b_share             double precision,
    fin17c_share             double precision,
    fin22d_share             double precision,
    fin22e_share             double precision,
    fin31a_31b_share         double precision,
    fin40a_share             double precision,
    fin41_share              double precision,
    fin35_share              double precision,
    digital_account_share    double precision,
    source_id                text NOT NULL DEFAULT 'GLOBAL_FINDEX',
    PRIMARY KEY (country_code, year, group_name, group_detail),
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_findex_country_year
    ON financial_inclusion_waves (country_code, year);

CREATE TABLE IF NOT EXISTS country_group_membership (
    country_code      char(3) NOT NULL,
    country_name      text NOT NULL,
    group_type        text NOT NULL,
    group_code        text NOT NULL,
    group_name        text NOT NULL,
    is_member         boolean NOT NULL DEFAULT true,
    source_id         text NOT NULL,
    valid_from        smallint,
    valid_to          smallint,
    notes             text,
    PRIMARY KEY (country_code, group_type, group_code),
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_country_group_membership_lookup
    ON country_group_membership (group_type, group_code, country_code);

CREATE TABLE IF NOT EXISTS source_coverage (
    source_id          text NOT NULL,
    dimension_name     text NOT NULL,
    category           text NOT NULL,
    observations       text,
    FOREIGN KEY (source_id) REFERENCES source_catalog(source_id)
);

CREATE INDEX IF NOT EXISTS ix_source_coverage_source
    ON source_coverage (source_id, dimension_name);

INSERT INTO source_catalog
    (source_id, source_name, version_label, source_url, period_start, period_end, notes)
VALUES
    ('WID', 'World Inequality Database', NULL, 'https://wid.world/', 2002, 2026,
     'Extratos selecionados de renda e concentração de riqueza.'),
    ('WIID', 'World Income Inequality Database - UNU-WIDER', NULL, 'https://www.wider.unu.edu/database/wiid', 2002, 2026,
     'Observações harmonizadas de desigualdade; não somar ao WID como observações independentes.'),
    ('ILOSTAT', 'ILOSTAT - Organização Internacional do Trabalho', 'Nov. 2025', 'https://ilostat.ilo.org/', 2002, 2026,
     'Rendimento do trabalho e diferença de gênero.'),
    ('PNAD', 'PNAD Contínua - IBGE', NULL, 'https://www.ibge.gov.br/estatisticas/sociais/trabalho.html', 2012, 2026,
     'Agregados ponderados por sexo e cor ou raça; 2026 contém T1 e T2 disponíveis.'),
    ('PNAD_CONTINUA', 'PNAD Contínua - IBGE (identificador de cobertura)', NULL, 'https://www.ibge.gov.br/estatisticas/sociais/trabalho.html', 2012, 2026,
     'Identificador usado no catálogo de cobertura do pipeline.'),
    ('GLOBAL_FINDEX', 'Global Findex - Banco Mundial', '2025 publication / 2024 wave', 'https://www.worldbank.org/en/publication/globalfindex', 2011, 2024,
     'Ondas de inclusão financeira; não é série anual contínua.'),
    ('VDEM', 'Varieties of Democracy', 'v16', 'https://www.v-dem.net/', 2002, 2025,
     'Indicadores institucionais e políticos por país-ano.'),
    ('METADATA', 'Catálogo de cobertura do projeto', NULL, NULL, 2002, 2026,
     'Metadados produzidos pelo pipeline do projeto.')
ON CONFLICT (source_id) DO UPDATE SET
    source_name = EXCLUDED.source_name,
    version_label = EXCLUDED.version_label,
    source_url = EXCLUDED.source_url,
    period_start = EXCLUDED.period_start,
    period_end = EXCLUDED.period_end,
    notes = EXCLUDED.notes,
    loaded_at = now();

COMMENT ON SCHEMA analytics IS 'Camada analítica compacta do projeto de desigualdade econômica.';
COMMENT ON TABLE brazil_pnad_group_income IS 'Agregados PNAD; os rendimentos permanecem nominais enquanto deflator_applied for false.';
COMMENT ON TABLE financial_inclusion_waves IS 'Ondas do Global Findex; *_share são proporções entre 0 e 1 quando disponíveis.';
COMMENT ON TABLE country_group_membership IS 'Grupos geográficos, socioeconômicos e de comparação documentados; não contém classificação capitalista/comunista.';


-- Views de consulta
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


-- Consultas de monitoramento
-- Consultas somente leitura para acompanhar o limite de armazenamento.
SET search_path TO analytics, public;

-- Tamanho total do banco.
SELECT
    current_database() AS database_name,
    pg_database_size(current_database()) AS database_bytes,
    pg_size_pretty(pg_database_size(current_database())) AS database_size;

-- Tamanho por tabela, incluindo índices e TOAST.
SELECT
    schemaname,
    relname AS table_name,
    pg_total_relation_size(relid) AS total_bytes,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS indexes_size
FROM pg_catalog.pg_statio_user_tables
WHERE schemaname = 'analytics'
ORDER BY pg_total_relation_size(relid) DESC;

-- Contagem e última estatística de cada tabela analítica.
SELECT
    schemaname,
    relname AS table_name,
    n_live_tup AS estimated_rows,
    last_analyze,
    last_autoanalyze
FROM pg_catalog.pg_stat_user_tables
WHERE schemaname = 'analytics'
ORDER BY n_live_tup DESC;
