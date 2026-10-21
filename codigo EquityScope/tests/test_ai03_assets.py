from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TestAI03Assets(unittest.TestCase):
    def test_terraform_files_exist(self):
        terraform_dir = ROOT / "infra" / "terraform"
        expected = {
            "versions.tf",
            "variables.tf",
            "main.tf",
            "outputs.tf",
            "terraform.tfvars.example",
            "README.md",
        }
        self.assertTrue(terraform_dir.is_dir())
        self.assertTrue(expected.issubset({p.name for p in terraform_dir.iterdir()}))

    def test_security_files_do_not_contain_real_credentials(self):
        files = [
            ROOT / ".gitignore",
            ROOT / "README.md",
            ROOT / "infra" / "terraform" / "terraform.tfvars.example",
            ROOT / "docs" / "infraestrutura_e_seguranca.md",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in files)
        self.assertIn("TF_VAR_aiven_api_token", text)
        self.assertIn("AIVEN_DATABASE_URL", text)
        self.assertIn("*.tfstate", text)
        self.assertNotIn("aiven_api_token = \"tok_", text)
        self.assertNotIn("postgres://avnadmin:", text)

    def test_readme_covers_ai03(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for term in ("Infraestrutura como código", "Segurança das informações", "Repositório e reprodução", "terraform validate"):
            self.assertIn(term, readme)


if __name__ == "__main__":
    unittest.main()
