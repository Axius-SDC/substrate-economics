#!/usr/bin/env python3
"""
Load an OASIS XML catalog into a `uri_mapper` callable for offline SDC4 validation.

The CordovaOS model schemas reference the SDC4 reference model (sdc4.xsd) by remote URL.
Rather than edit the canonical, byte-identical model schemas, we collocate the complete
SDCRM in this repo (benchmarks/sdcrm/) and ship an OASIS catalog (benchmarks/catalog.xml)
that maps the SDC4 URIs to those local copies. `sdcvalidator`/`xmlschema` accept the
resulting mapper via their `uri_mapper` argument, so validation runs fully offline against
unmodified schemas.

Supports OASIS `uri`/`system` (exact) and `rewriteURI`/`rewriteSystem` (prefix) entries.
"""
from __future__ import annotations

import pathlib
import xml.etree.ElementTree as ET
from typing import Callable

_NS = "{urn:oasis:names:tc:entity:xmlns:xml:catalog}"


def load_catalog(catalog_path: str | pathlib.Path) -> Callable[[str], str]:
    """Parse an OASIS catalog and return a callable mapping remote URIs to local file URIs."""
    catalog_path = pathlib.Path(catalog_path).resolve()
    base = catalog_path.parent
    root = ET.parse(catalog_path).getroot()

    def local_uri(target: str) -> str:
        p = pathlib.Path(target)
        p = p if p.is_absolute() else (base / p)
        return p.resolve().as_uri()

    exact: dict[str, str] = {}
    for tag, key in ((f"{_NS}uri", "name"), (f"{_NS}system", "systemId")):
        for e in root.iter(tag):
            exact[e.get(key)] = local_uri(e.get("uri"))

    prefixes: list[tuple[str, str]] = []
    for tag, key in ((f"{_NS}rewriteURI", "uriStartString"),
                     (f"{_NS}rewriteSystem", "systemIdStartString")):
        for e in root.iter(tag):
            prefixes.append((e.get(key), e.get("rewritePrefix")))
    # longest start string first, so the most specific rule wins
    prefixes.sort(key=lambda t: len(t[0]), reverse=True)

    def mapper(uri: str) -> str:
        if uri in exact:
            return exact[uri]
        for start, rewrite in prefixes:
            if uri.startswith(start):
                return local_uri(rewrite + uri[len(start):])
        return uri  # unmapped -> leave unchanged

    return mapper


if __name__ == "__main__":
    import sys
    m = load_catalog(sys.argv[1] if len(sys.argv) > 1 else "catalog.xml")
    test = "https://semanticdatacharter.com/ns/sdc4/sdc4.xsd"
    print(f"{test} -> {m(test)}")
