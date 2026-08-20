#!/usr/bin/env python3
"""Deterministic content, locale, link and claim validation for inQRedible."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "content" / "release-content.json"
MATRIX_PATH = ROOT / "content" / "2.5.0-content-matrix.md"


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.title_parts: list[str] = []
        self.in_title = False
        self.canonical: list[str] = []
        self.alternates: dict[str, str] = {}
        self.hrefs: list[str] = []
        self.sources: list[str] = []
        self.ids: list[str] = []
        self.sections: list[str] = []
        self.images_without_alt = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = values.get("lang", "")
        if tag == "title":
            self.in_title = True
        if tag == "link":
            rel = values.get("rel", "").split()
            if "canonical" in rel:
                self.canonical.append(values.get("href", ""))
            if "alternate" in rel and values.get("hreflang"):
                self.alternates[values["hreflang"]] = values.get("href", "")
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        if tag in {"img", "script", "link"}:
            source = values.get("src") or (values.get("href") if tag == "link" and values.get("rel") == "stylesheet" else "")
            if source:
                self.sources.append(source)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "section" and values.get("data-section"):
            self.sections.append(values["data-section"])
        if tag == "img" and "alt" not in values:
            self.images_without_alt += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def load_manifest(root: Path = ROOT) -> dict:
    return json.loads((root / "content" / "release-content.json").read_text(encoding="utf-8"))


def render_matrix(manifest: dict) -> str:
    routes = manifest["routes"]
    lines = [
        "# inQRedible 2.5.0 website content matrix",
        "",
        "Generated from `content/release-content.json`; do not edit manually.",
        "",
        f"- Legal/content version: `{manifest['legal_version']}`",
        f"- App release source: `{manifest['source']['release_branch_sha']}`",
        f"- Material legal review: `{manifest['publication']['material_legal_review']}`",
        f"- Live validation owner: `{manifest['publication']['live_validation_owner']}`",
        "",
        "## Canonical routes",
        "",
        "| Locale | Home | Privacy | Terms | Support |",
        "| --- | --- | --- | --- | --- |",
    ]
    for locale in ("en", "es"):
        row = routes[locale]
        lines.append(f"| {locale} | {row['home']} | {row['privacy']} | {row['terms']} | {row['support']} |")
    lines.extend(["", "## FREE / PRO matrix", "", "| Capability | FREE | PRO |", "| --- | :---: | :---: |"])
    for item in manifest["feature_matrix"]:
        lines.append(f"| `{item['id']}` | {'Yes' if item['free'] else 'No'} | {'Yes' if item['pro'] else 'No'} |")
    lines.extend(["", "## Provider boundaries", "", "| Provider | Consent | Retention boundary |", "| --- | --- | --- |"])
    for provider in manifest["providers"]:
        lines.append(f"| {provider['name']} | `{provider['consent']}` | `{provider['retention']}` |")
    lines.extend(["", "## Claim boundaries", ""])
    for name, boundary in sorted(manifest["claim_boundaries"].items()):
        lines.append(f"- `{name}`: `{boundary}`")
    return "\n".join(lines) + "\n"


def prohibited_claim_errors(text: str, filename: str) -> list[str]:
    checks = {
        "unconditional trial": r"\b(3 days free|3 días gratis|free 3-day trial|prueba gratuita de 3 días)\b",
        "static JSON-LD price": r'"price(?:Currency)?"\s*:',
        "press-ready claim": r"\b(press[- ]ready|print[- ]ready|list[oa] para imprenta)\b",
        "zero-collection claim": r"\b(zero data collection|collects no data|no data collected|cero recogida de datos|no recoge datos)\b",
        "cloud-sync promise": r"\b(includes cloud sync|cloud backup included|incluye sincronización en la nube)\b",
        "lifetime promotion": r"\b(buy lifetime|lifetime plan|lifetime purchase available|compra vitalicia disponible|plan vitalicio)\b",
        "absolute scanner safety": r"\b(guaranteed safe|certified safe|garantizado como seguro|certificado como seguro)\b",
    }
    lowered = text.casefold()
    errors: list[str] = []
    for name, pattern in checks.items():
        for match in re.finditer(pattern, lowered, re.IGNORECASE):
            prefix = lowered[max(0, match.start() - 32):match.start()]
            if re.search(r"\b(?:no|not|never|without|isn't|doesn't)\b[^.!?]{0,24}$", prefix):
                continue
            errors.append(f"{filename}: prohibited {name}")
            break
    return errors


def local_target(root: Path, page: Path, reference: str) -> tuple[Path, str] | None:
    parsed = urlparse(reference)
    if parsed.scheme or parsed.netloc or reference.startswith(("mailto:", "tel:", "javascript:")):
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        target = page
    elif path_text.startswith("/"):
        target = root / path_text.lstrip("/")
    else:
        target = page.parent / path_text
    if target.is_dir():
        target /= "index.html"
    return target.resolve(), parsed.fragment


def parse_documents(root: Path) -> tuple[dict[Path, Document], list[str]]:
    documents: dict[Path, Document] = {}
    errors: list[str] = []
    for page in sorted(root.rglob("*.html")):
        if any(part.startswith(".") for part in page.relative_to(root).parts):
            continue
        parser = Document()
        text = page.read_text(encoding="utf-8")
        try:
            parser.feed(text)
        except Exception as exc:
            errors.append(f"{page.relative_to(root)}: HTML parse failed: {exc}")
            continue
        documents[page.resolve()] = parser
        name = str(page.relative_to(root))
        if not parser.lang:
            errors.append(f"{name}: missing html lang")
        if not parser.title:
            errors.append(f"{name}: missing title")
        if len(parser.canonical) != 1:
            errors.append(f"{name}: expected exactly one canonical link")
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f"{name}: duplicate id")
        if parser.images_without_alt:
            errors.append(f"{name}: image missing alt attribute")
        errors.extend(prohibited_claim_errors(text, name))
    return documents, errors


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    expected_top = {"schema_version", "release", "legal_version", "effective_date", "source", "publication", "routes", "storekit", "feature_matrix", "providers", "consent", "telemetry_forbidden", "claim_boundaries", "required_home_claims"}
    missing = expected_top - manifest.keys()
    if missing:
        errors.append(f"manifest: missing keys {sorted(missing)}")
    if manifest.get("release") != "2.5.0" or manifest.get("legal_version") != "legal-2.5.0-v1":
        errors.append("manifest: wrong release or legal version")
    features = {item["id"]: item for item in manifest.get("feature_matrix", [])}
    if features.get("scanner_warned_links", {}).get("free") is not True:
        errors.append("manifest: warned-link scanner must be FREE")
    if features.get("professional_export", {}).get("free") is not False:
        errors.append("manifest: professional export must be PRO")
    if manifest.get("storekit", {}).get("displayed_products") != ["weekly", "yearly"]:
        errors.append("manifest: displayed StoreKit products drifted")
    if len({provider["name"] for provider in manifest.get("providers", [])}) != 4:
        errors.append("manifest: expected four distinct optional providers")
    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    manifest = load_manifest(root)
    errors = validate_manifest(manifest)
    documents, html_errors = parse_documents(root)
    errors.extend(html_errors)

    for page, doc in documents.items():
        name = str(page.relative_to(root))
        for reference in doc.hrefs + doc.sources:
            target_info = local_target(root, page, reference)
            if target_info is None:
                continue
            target, fragment = target_info
            try:
                target.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{name}: local reference escapes repository: {reference}")
                continue
            if not target.exists():
                errors.append(f"{name}: broken local reference: {reference}")
                continue
            if fragment and target.suffix == ".html":
                target_doc = documents.get(target)
                if target_doc and fragment not in target_doc.ids:
                    errors.append(f"{name}: missing fragment #{fragment} in {target.relative_to(root)}")

    route_pairs = (("home", "index.html", "es/index.html"), ("privacy", "privacy.html", "es/privacy.html"), ("terms", "terms.html", "es/terms.html"), ("support", "support.html", "es/soporte.html"))
    for key, en_path, es_path in route_pairs:
        en_doc = documents[(root / en_path).resolve()]
        es_doc = documents[(root / es_path).resolve()]
        expected_en = manifest["routes"]["en"][key]
        expected_es = manifest["routes"]["es"][key]
        if en_doc.canonical != [expected_en] or es_doc.canonical != [expected_es]:
            errors.append(f"{key}: canonical route drift")
        required_alternates = {"en": expected_en, "es": expected_es, "x-default": expected_en}
        if en_doc.alternates != required_alternates or es_doc.alternates != required_alternates:
            errors.append(f"{key}: hreflang parity drift")
        if key != "home" and en_doc.sections != es_doc.sections:
            errors.append(f"{key}: semantic section parity drift")

    for locale, page_name in (("en", "index.html"), ("es", "es/index.html")):
        text = (root / page_name).read_text(encoding="utf-8")
        for claim in manifest["required_home_claims"][locale]:
            if claim.casefold() not in text.casefold():
                errors.append(f"{page_name}: missing required claim {claim!r}")

    for page_name in ("privacy.html", "es/privacy.html"):
        text = (root / page_name).read_text(encoding="utf-8")
        for provider in manifest["providers"]:
            if provider["name"].casefold() not in text.casefold():
                errors.append(f"{page_name}: missing provider {provider['name']}")
        for url in ("https://firebase.google.com/support/privacy", "https://policies.google.com/privacy"):
            if url not in text:
                errors.append(f"{page_name}: missing provider policy link {url}")

    for page_name in ("privacy.html", "es/privacy.html", "terms.html", "es/terms.html", "support.html", "es/soporte.html"):
        if manifest["legal_version"] not in (root / page_name).read_text(encoding="utf-8"):
            errors.append(f"{page_name}: missing legal version")

    sitemap = ElementTree.parse(root / "sitemap.xml")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = {node.text for node in sitemap.findall(".//sm:loc", namespace)}
    for locale in ("en", "es"):
        for url in manifest["routes"][locale].values():
            if url not in locations:
                errors.append(f"sitemap.xml: missing {url}")

    expected_matrix = render_matrix(manifest)
    actual_matrix = (root / "content" / "2.5.0-content-matrix.md").read_text(encoding="utf-8")
    if actual_matrix != expected_matrix:
        errors.append("content matrix is stale; run scripts/check_content.py --write-matrix")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-matrix", action="store_true")
    args = parser.parse_args()
    if args.write_matrix:
        MATRIX_PATH.write_text(render_matrix(load_manifest()), encoding="utf-8")
    errors = validate_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Content validation passed: manifest, EN/ES parity, canonical routes, local links, claims and generated matrix.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
