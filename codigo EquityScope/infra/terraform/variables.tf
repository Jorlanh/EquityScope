variable "aiven_api_token" {
  description = "Token da API da Aiven. Deve ser fornecido por TF_VAR_aiven_api_token ou por um arquivo local ignorado pelo Git."
  type        = string
  sensitive   = true
}

variable "aiven_project" {
  description = "Nome do projeto já criado na Aiven."
  type        = string
}

variable "aiven_plan" {
  description = "Plano do serviço PostgreSQL. Confira o identificador exibido na sua conta antes do apply."
  type        = string
  default     = "free-1-1gb"
}

variable "aiven_cloud_name" {
  description = "Cloud/região do serviço. Deixe nulo no plano Free, que escolhe a localização automaticamente."
  type        = string
  default     = null
  nullable    = true
}

variable "service_name" {
  description = "Nome do serviço PostgreSQL na Aiven."
  type        = string
  default     = "equityscope-postgresql"
}

variable "database_name" {
  description = "Banco lógico que receberá o schema analytics."
  type        = string
  default     = "analyticsdb"
}

variable "enable_public_access" {
  description = "Permite conexão PostgreSQL pela Internet com TLS e credenciais. Necessário para carga local sem rede privada."
  type        = bool
  default     = true
}

variable "termination_protection" {
  description = "Evita que um terraform destroy remova o serviço sem alteração explícita do código."
  type        = bool
  default     = true
}
