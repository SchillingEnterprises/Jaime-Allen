"""Guard the public Jekyll boundary around the separate therapy prototype."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PublicPublicationBoundaryTests(unittest.TestCase):
    def test_jekyll_excludes_the_entire_therapy_application(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        self.assertRegex(config, r"(?m)^\s*-\s+therapy_site/\s*$")
        self.assertRegex(config, r'(?m)^\s*-\s+"\*\*/\*\.sqlite3"\s*$')
        self.assertRegex(config, r'(?m)^\s*-\s+"\*\*/\*\.sqlite3-journal"\s*$')
        self.assertRegex(config, r'(?m)^\s*-\s+"\*\*/\*\.sqlite3-wal"\s*$')
        self.assertRegex(config, r'(?m)^\s*-\s+"\*\*/\*\.sqlite3-shm"\s*$')

    def test_pages_workflow_does_not_build_or_publish_the_django_app(self):
        workflow_dir = ROOT / ".github" / "workflows"
        workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(workflow_dir.glob("*.yml"))
        )
        self.assertIn("static-site-validation.yml", workflows)
        self.assertNotRegex(workflows, r"(?m)^\s*-\s*therapy_site/\*\*")
        self.assertNotIn("working-directory: therapy_site", workflows)


if __name__ == "__main__":
    unittest.main()
