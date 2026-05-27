#!/usr/bin/env python3
"""
Vendor the CordovaOS government models into this repo as offline benchmark fixtures.

CordovaOS (https://github.com/Axius-SDC/CordovaOS, Apache-2.0) publishes ten cross-domain
government registries, each as an SDC4 XSD + SHACL shapes (.ttl) + JSON-LD + an XML instance
template. Those schemas reference the SDC4 reference model (sdc4.xsd) by REMOTE URL, which
breaks offline reproduction. This script copies each model's artifacts into
`benchmarks/fixtures/<Model>/`, rewrites the remote `sdc4.xsd` include to a local relative
path, and vendors a single self-contained copy of `sdc4.xsd`.

Run ONCE (by a maintainer with a CordovaOS checkout and the SDCRM sdc4.xsd) to regenerate the
committed fixtures. Cloners do NOT need to run this — the fixtures are committed, so the
benchmark runs offline straight from a clone.
"""
import argparse
import shutil
from pathlib import Path

REMOTE_INCLUDE = 'schemaLocation="https://semanticdatacharter.com/ns/sdc4/sdc4.xsd"'
LOCAL_INCLUDE = 'schemaLocation="../sdc4.xsd"'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cordova", default="/home/twcook/GitHub/CordovaOS",
                    help="Path to a CordovaOS checkout (source of the ten models).")
    ap.add_argument("--sdc4", default="/media/twcook/SDCBackup/Github/SDCRM/sdc4/schemas/sdc4.xsd",
                    help="Path to the self-contained SDC4 reference schema (SDCRM).")
    ap.add_argument("--out", default=str(Path(__file__).parent / "fixtures"),
                    help="Output fixtures directory inside this repo.")
    args = ap.parse_args()

    cordova = Path(args.cordova)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    shutil.copy(args.sdc4, out / "sdc4.xsd")
    print(f"vendored sdc4.xsd -> {out / 'sdc4.xsd'}")

    models_dir = cordova / "models"
    count = 0
    for d in sorted(p for p in models_dir.iterdir() if p.is_dir()):
        xsd = next(iter(d.glob("dm-*.xsd")), None)
        if xsd is None:
            continue
        stem = xsd.stem  # dm-<cuid>
        dest = out / d.name
        dest.mkdir(exist_ok=True)

        text = xsd.read_text(encoding="utf-8")
        if REMOTE_INCLUDE not in text:
            print(f"  WARN {d.name}: expected remote sdc4 include not found; leaving as-is")
        text = text.replace(REMOTE_INCLUDE, LOCAL_INCLUDE)
        (dest / xsd.name).write_text(text, encoding="utf-8")

        for suffix in ("_shacl.ttl", ".jsonld", ".xml", ".sha1"):
            src = d / f"{stem}{suffix}"
            if src.exists():
                shutil.copy(src, dest / src.name)

        count += 1
        print(f"  vendored {d.name} ({stem})")

    print(f"done: {count} models -> {out}")


if __name__ == "__main__":
    main()
