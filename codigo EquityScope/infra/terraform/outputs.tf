output "postgresql_service_uri" {
  description = "URI TLS para conexão com o PostgreSQL. O valor é sensível e não deve ser publicado."
  value       = aiven_pg.analytics.service_uri
  sensitive   = true
}

output "service_name" {
  description = "Nome do serviço criado na Aiven."
  value       = aiven_pg.analytics.service_name
}

output "database_name" {
  description = "Nome do banco lógico criado na Aiven."
  value       = aiven_pg_database.analytics.database_name
}

output "next_step" {
  description = "Próximo passo após a infraestrutura estar disponível."
  value       = "Execute sql/aiven_postgresql_completo.sql e depois python src/14_carregar_aiven.py --replace com AIVEN_DATABASE_URL definido."
}
