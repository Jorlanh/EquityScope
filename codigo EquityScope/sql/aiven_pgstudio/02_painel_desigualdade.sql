-- Execute depois de 01_catalogo.sql.
SET search_path TO analytics, public;

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
