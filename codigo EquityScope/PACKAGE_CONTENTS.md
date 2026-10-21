# Conteúdo do pacote técnico

Este pacote contém somente os arquivos necessários para reproduzir o tratamento, consultar os dados tratados e preparar a carga na Aiven.

## Incluído

- `run_pipeline.py` e os scripts de `src/`;
- `data/processed/`, `data/metadata/` e arquivos de apoio;
- `frontend/` com o painel;
- `sql/` com schema, views e monitoramento;
- `infra/terraform/` com o provisionamento da Aiven;
- `docs/` com a documentação;
- `tests/` com os testes automatizados;
- `outputs/tables/`, `outputs/figures/`, `outputs/reports/` e `outputs/statistical_tests/`.

## Não incluído

- o ZIP bruto de aproximadamente 8 GB;
- `.venv`;
- credenciais e arquivos `.tfvars` locais;
- estado do Terraform;
- arquivos antigos duplicados de Word, PDF e ZIP;
- scripts auxiliares de divisão do ZIP bruto.

O pacote técnico é separado do arquivo Word da entrega escrita. A criação e a carga reais na Aiven precisam ser feitas com as credenciais da equipe.
