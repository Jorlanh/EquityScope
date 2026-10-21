-- Execute depois de 04_grupos_findex_cobertura.sql.
SET search_path TO analytics, public;

COMMENT ON SCHEMA analytics IS 'Camada analítica compacta do projeto de desigualdade econômica.';
COMMENT ON TABLE brazil_pnad_group_income IS 'Agregados PNAD; os rendimentos permanecem nominais enquanto deflator_applied for false.';
COMMENT ON TABLE financial_inclusion_waves IS 'Ondas do Global Findex; *_share são proporções entre 0 e 1 quando disponíveis.';
COMMENT ON TABLE country_group_membership IS 'Grupos geográficos, socioeconômicos e de comparação documentados; não contém classificação capitalista/comunista.';
