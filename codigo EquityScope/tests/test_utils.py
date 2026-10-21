import unittest

from src.utils import load_config, normalize_label, parse_year


class UtilsTest(unittest.TestCase):
    def test_normalize_label(self):
        self.assertEqual(normalize_label("São Tomé e Príncipe"), "sao_tome_e_principe")

    def test_parse_year(self):
        self.assertEqual(parse_year("PNADC_022026.zip"), 2026)
        self.assertIsNone(parse_year("sem ano"))

    def test_raw_source_is_project_relative(self):
        config = load_config()
        self.assertEqual(config["sources"]["source_zip"], "data/raw/dados para bigdata.zip")


if __name__ == "__main__":
    unittest.main()
