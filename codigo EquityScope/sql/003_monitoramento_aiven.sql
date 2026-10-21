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
