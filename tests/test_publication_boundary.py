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

    def test_therapy_sqlite_database_is_not_tracked_or_reintroduced(self):
        database = ROOT / "therapy_site" / "db.sqlite3"
        self.assertFalse(database.exists(), "The potentially sensitive historical DB must stay out of the current tree.")

        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("*.sqlite3", ignore)
        self.assertIn("*.sqlite", ignore)
        workflow = (
            ROOT / ".github" / "workflows" / "sqlite-privacy-metadata.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("Allow only removal of the historical tracked SQLite file", workflow)
        self.assertIn("never modified or replaced", workflow)

    def test_static_site_validation_is_separate_from_django_ci(self):
        workflow = (
            ROOT / ".github" / "workflows" / "static-site-validation.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("name: Jaime static-site validation", workflow)
        self.assertNotIn("therapy_site/**", workflow)
        self.assertNotIn("working-directory: therapy_site", workflow)


if __name__ == "__main__":
    unittest.main()
