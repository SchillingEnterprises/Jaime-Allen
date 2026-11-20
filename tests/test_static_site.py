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
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
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

    def test_react_homepage_has_keyboard_skip_navigation_and_main_landmark(self):
        page = ROOT / "index.html"
        parser = LocalReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))

        self.assertIn(
            ("a", {"class": "skip-link", "href": "#main"}),
            parser.elements,
        )
        self.assertIn(
            ("div", {"id": "root", "tabindex": "-1"}),
            parser.elements,
        )
        self.assertTrue(
            any(tag == "main" and attrs.get("id") == "main" for tag, attrs in parser.elements),
            "The skip link must target a real main-content fallback.",
        )
        self.assertIn("The interactive presentation is loading.", page.read_text(encoding="utf-8"))
        self.assertIn('y("main",{id:"main",tabIndex:-1', page.read_text(encoding="utf-8"))
        source = page.read_text(encoding="utf-8")
        self.assertIn(".skip-link:focus", source)
        self.assertIn("#main:focus", source)

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

    def test_public_profile_matches_the_current_practice_listing(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        for expected in (
            "Licensed Marriage & Family Therapist",
            "LMFT #164998",
            "Insightful Matters Family Counseling Professionals",
            "Virtual telehealth",
            "https://www.insightfulmatters.com/jaime-allen",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, source)

        for retired in (
            "AMFT #163181",
            "JaimeAllen777",
            "paypal.me/FairyAstrology",
            "SolarisFairyAstrology@yahoo.com",
            "Professional profile update pending",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, source)

    def test_legacy_biography_and_archive_disclose_current_scope(self):
        biography = (ROOT / "website" / "page sections" / "about" / "jaime_allen.html").read_text(encoding="utf-8")
        archive = (ROOT / "foyer_index.html").read_text(encoding="utf-8")
        self.assertIn("LMFT #164998", biography)
        self.assertIn("Insightful Matters Family Counseling Professionals", biography)
        self.assertIn("historical educational resource archive", archive)
        self.assertIn("https://www.insightfulmatters.com/jaime-allen", archive)

    def test_research_index_discloses_static_educational_scope(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("Educational Topic Index — Static Demonstration", source)
        self.assertIn("does not use AI agents", source)
        self.assertIn("does not provide personalized clinical guidance", source)
        for unsupported_claim in ("60% reduction", "75% couples report", "70-75% move", "N=2,231"):
            with self.subTest(unsupported_claim=unsupported_claim):
                self.assertNotIn(unsupported_claim, source)

    def test_reflection_does_not_advertise_secure_sharing_or_a_client_portal(self):
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("No secure sharing or client portal is available here", source)
        self.assertIn("Do not enter names, identifying details, or sensitive health information.", source)
        self.assertIn("This page cannot securely transmit or store my report.", source)
        self.assertNotIn("Optional, Secure", source)
        self.assertNotIn("secure client portal verified", source)


if __name__ == "__main__":
    unittest.main()
