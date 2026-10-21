-- Execute este arquivo primeiro no PG Studio.
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

INSERT INTO source_catalog
    (source_id, source_name, version_label, source_url, period_start, period_end, notes)
VALUES
    ('WID', 'World Inequality Database', NULL, 'https://wid.world/', 2002, 2026, 'Extratos selecionados de renda e concentração de riqueza.'),
    ('WIID', 'World Income Inequality Database - UNU-WIDER', NULL, 'https://www.wider.unu.edu/database/wiid', 2002, 2026, 'Observações harmonizadas de desigualdade; não somar ao WID como observações independentes.'),
    ('ILOSTAT', 'ILOSTAT - Organização Internacional do Trabalho', 'Nov. 2025', 'https://ilostat.ilo.org/', 2002, 2026, 'Rendimento do trabalho e diferença de gênero.'),
    ('PNAD', 'PNAD Contínua - IBGE', NULL, 'https://www.ibge.gov.br/estatisticas/sociais/trabalho.html', 2012, 2026, 'Agregados ponderados por sexo e cor ou raça; 2026 contém T1 e T2 disponíveis.'),
    ('PNAD_CONTINUA', 'PNAD Contínua - IBGE (identificador de cobertura)', NULL, 'https://www.ibge.gov.br/estatisticas/sociais/trabalho.html', 2012, 2026, 'Identificador usado no catálogo de cobertura do pipeline.'),
    ('GLOBAL_FINDEX', 'Global Findex - Banco Mundial', '2025 publication / 2024 wave', 'https://www.worldbank.org/en/publication/globalfindex', 2011, 2024, 'Ondas de inclusão financeira; não é série anual contínua.'),
    ('VDEM', 'Varieties of Democracy', 'v16', 'https://www.v-dem.net/', 2002, 2025, 'Indicadores institucionais e políticos por país-ano.'),
    ('METADATA', 'Catálogo de cobertura do projeto', NULL, NULL, 2002, 2026, 'Metadados produzidos pelo pipeline do projeto.')
ON CONFLICT (source_id) DO UPDATE SET
    source_name = EXCLUDED.source_name,
    version_label = EXCLUDED.version_label,
    source_url = EXCLUDED.source_url,
    period_start = EXCLUDED.period_start,
    period_end = EXCLUDED.period_end,
    notes = EXCLUDED.notes,
    loaded_at = now();
