# Dados brutos

O pipeline espera encontrar aqui `dados para bigdata.zip`.

O arquivo original tem cerca de 8,1 GB e não é versionado no repositório principal. Para usar os dados completos, coloque o ZIP nesta pasta ou baixe as partes da Release do GitHub e execute:

```powershell
python scripts/join_raw_archive.py --input-dir data/raw --output "data/raw/dados para bigdata.zip"
```

Depois, execute `python run_pipeline.py` na raiz do projeto. Qualquer seleção, conversão ou limpeza deve ser gravada em `data/interim/` ou `data/processed/`.
