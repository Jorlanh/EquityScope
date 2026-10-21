-- Execute depois de 02_painel_desigualdade.sql.
SET search_path TO analytics, public;

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
