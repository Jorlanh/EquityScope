from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_loader_module():
    path = ROOT / "src" / "14_carregar_aiven.py"
    spec = importlib.util.spec_from_file_location("aiven_loader", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AivenAssetsTest(unittest.TestCase):
    def test_aiven_sql_and_views_exist(self):
        schema = (ROOT / "sql" / "001_schema_aiven.sql").read_text(encoding="utf-8")
        views = (ROOT / "sql" / "002_views_aiven.sql").read_text(encoding="utf-8")
        for table in (
            "source_catalog",
            "country_year_panel",
            "wid_income_distribution",
            "wid_wealth_concentration",
            "wiid_inequality",
            "labor_gender_gap",
            "labor_gender_modelled",
            "brazil_pnad_group_income",
            "financial_inclusion_waves",
            "country_group_membership",
            "source_coverage",
        ):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", schema)
        self.assertIn("v_pnad_latest_by_group", views)
        self.assertIn("v_country_year_context", views)

    def test_aiven_loader_points_to_existing_processed_extracts(self):
        module = load_loader_module()
        self.assertEqual(len(module.SPECS), 10)
        self.assertTrue(all(spec.path.exists() for spec in module.SPECS))
        panel = next(spec for spec in module.SPECS if spec.table == "country_year_panel")
        rows = []
        with panel.path.open(encoding="utf-8-sig", newline="") as handle:
            import csv

            reader = csv.DictReader(handle)
            for row in reader:
                if len(rows) >= 10:
                    break
                rows.append(module.row_panel(row))
        self.assertTrue(all(row[0] for row in rows))

    def test_country_comparison_groups_are_documented(self):
        path = ROOT / "data" / "processed" / "country_group_membership.csv"
        self.assertTrue(path.exists())
        import csv

        with path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        group_types = {row["group_type"] for row in rows}
        self.assertIn("un_region", group_types)
        self.assertIn("world_bank_region", group_types)
        self.assertIn("income_group", group_types)
        self.assertNotIn("economic_system", group_types)
        self.assertNotIn("government_orientation", group_types)

    def test_pgstudio_scripts_respect_ten_command_limit(self):
        scripts = sorted((ROOT / "sql" / "aiven_pgstudio").glob("*.sql"))
        self.assertEqual(len(scripts), 7)
        for path in scripts:
            self.assertLessEqual(path.read_text(encoding="utf-8").count(";"), 10, path.name)

    def test_complete_postgresql_script_contains_schema_views_and_monitoring(self):
        path = ROOT / "sql" / "aiven_postgresql_completo.sql"
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS source_catalog", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS country_group_membership", content)
        self.assertIn("CREATE OR REPLACE VIEW v_country_comparison_context", content)
        self.assertIn("pg_database_size(current_database())", content)

    def test_frontend_files_exist_and_expose_main_filters(self):
        app = ROOT / "frontend" / "app.py"
        self.assertTrue(app.exists())
        content = app.read_text(encoding="utf-8")
        for label in ("Países", "Período", "Sexo", "Raça/cor", "Indicador"):
            self.assertIn(label, content)
        self.assertIn('hovermode="x unified"', content)
        self.assertIn('on_select="rerun"', content)
        self.assertIn("Clique na legenda para ocultar ou exibir séries", content)
        self.assertTrue((ROOT / "frontend" / "README.md").exists())
        self.assertTrue((ROOT / "requirements-frontend.txt").exists())
