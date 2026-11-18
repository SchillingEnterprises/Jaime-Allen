"""Dependency-free smoke tests for the repository's static Jaime Allen pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LocalReferenceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append((tag, name, value))


class StaticProjectSmokeTests(unittest.TestCase):
    def test_both_project_surfaces_are_present(self):
        required = (
            ROOT / "index.html",
            ROOT / "foyer_index.html",
            ROOT / "website" / "static" / "css" / "styles.css",
            ROOT / "website" / "page sections" / "about" / "jaime_allen.html",
            ROOT / "therapy_site" / "manage.py",
            ROOT / "therapy_site" / "requirements.txt",
        )
        for path in required:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), f"Missing project file: {path.relative_to(ROOT)}")

    def test_legacy_static_page_local_references_resolve(self):
        page = ROOT / "foyer_index.html"
        parser = LocalReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        missing = []

        for tag, attribute, reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or reference.startswith(("#", "//")):
                continue
            local_path = unquote(parsed.path)
            if not local_path:
                continue
            target = (ROOT / local_path).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():
                missing.append(f"{tag}[{attribute}]={reference}")

        self.assertEqual([], missing, "Broken local links/assets in foyer_index.html: " + ", ".join(missing))


if __name__ == "__main__":
    unittest.main()
