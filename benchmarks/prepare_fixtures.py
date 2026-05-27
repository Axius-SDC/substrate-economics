#!/usr/bin/env python3
"""
Vendor the offline benchmark fixtures: the complete SDCRM, the ten CordovaOS models
(byte-identical, unmodified), and an OASIS catalog that resolves the models' remote SDC4
references to the collocated SDCRM.

Why a catalog instead of editing the schemas: the CordovaOS model schemas reference the
SDC4 reference model by remote URL. The correct, faithful way to validate them offline is to
collocate the complete (open-source, Apache-2.0) SDCRM and provide an OASIS `catalog.xml`
that maps the SDC4 URIs to the local copies. The model schemas stay exactly as CordovaOS
published them; only URI resolution is redirected. See `sdc_catalog.py`.

Run ONCE (by a maintainer with CordovaOS and SDCRM checkouts) to regenerate the committed
fixtures. Cloners do NOT need it — everything required is committed and the benchmark runs
offline from a clone.

Layout produced:
  benchmarks/sdcrm/sdc4/schemas/...        complete SDCRM reference model (collocated)
  benchmarks/fixtures/<Model>/dm-*.xsd     CordovaOS models, UNMODIFIED, + .ttl/.jsonld/.xml
  benchmarks/catalog.xml                    OASIS catalog: SDC4 URIs -> sdcrm/
"""
import argparse
import shutil
from pathlib import Path

SDC4_NS_BASE = "https://semanticdatacharter.com/ns/sdc4/"
CATALOG_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!-- OASIS XML catalog: redirects SDC4 reference-model URIs to the collocated SDCRM. -->
<!-- The CordovaOS model schemas are left byte-identical; only resolution is redirected. -->
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <rewriteURI uriStartString="{base}" rewritePrefix="sdcrm/sdc4/schemas/"/>
  <rewriteSystem systemIdStartString="{base}" rewritePrefix="sdcrm/sdc4/schemas/"/>
  <uri name="{base}sdc4.xsd" uri="sdcrm/sdc4/schemas/sdc4.xsd"/>
  <system systemId="{base}sdc4.xsd" uri="sdcrm/sdc4/schemas/sdc4.xsd"/>
</catalog>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cordova", default="/home/twcook/GitHub/CordovaOS",
                    help="CordovaOS checkout (source of the ten models).")
    ap.add_argument("--sdcrm-schemas", default="/media/twcook/SDCBackup/Github/SDCRM/sdc4/schemas",
                    help="Path to the SDCRM sdc4/schemas directory (the reference model).")
    ap.add_argument("--bench", default=str(Path(__file__).parent),
                    help="benchmarks/ directory in this repo.")
    args = ap.parse_args()

    bench = Path(args.bench)
    fixtures = bench / "fixtures"
    sdcrm_dest = bench / "sdcrm" / "sdc4" / "schemas"

    # 1. collocate the complete SDCRM (reference schemas + OWL/TTL semantic layer)
    if sdcrm_dest.exists():
        shutil.rmtree(sdcrm_dest)
    shutil.copytree(args.sdcrm_schemas, sdcrm_dest)
    print(f"collocated SDCRM -> {sdcrm_dest} ({len(list(sdcrm_dest.iterdir()))} files)")

    # 2. vendor the ten CordovaOS models UNMODIFIED
    if fixtures.exists():
        shutil.rmtree(fixtures)
    fixtures.mkdir(parents=True)
    models_dir = Path(args.cordova) / "models"
    count = 0
    for d in sorted(p for p in models_dir.iterdir() if p.is_dir()):
        xsd = next(iter(d.glob("dm-*.xsd")), None)
        if xsd is None:
            continue
        stem = xsd.stem
        dest = fixtures / d.name
        dest.mkdir()
        for suffix in (".xsd", "_shacl.ttl", ".jsonld", ".xml", ".sha1"):
            src = d / f"{stem}{suffix}"
            if src.exists():
                shutil.copy(src, dest / src.name)  # byte-identical copy, no rewrite
        count += 1
        print(f"  vendored {d.name} ({stem}) [unmodified]")

    # 3. write the OASIS catalog
    (bench / "catalog.xml").write_text(CATALOG_TEMPLATE.format(base=SDC4_NS_BASE), encoding="utf-8")
    print(f"wrote {bench / 'catalog.xml'}")
    print(f"done: {count} models")


if __name__ == "__main__":
    main()
