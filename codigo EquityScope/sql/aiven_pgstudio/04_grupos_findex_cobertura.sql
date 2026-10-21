-- Execute depois de 03_trabalho_pnad.sql.
SET search_path TO analytics, public;

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
