#!/usr/bin/env python3
"""
Schema-driven generator of valid, governance-populated SDC4 instances.

Walks a model's XSD content model and emits a schema-valid value for every required leaf
(enumeration -> an allowed value, dateTime -> a valid timestamp, XdOrdinal -> ordinal+symbol,
etc.), picking a single branch at choices, and respecting namespace qualification from the
schema (`XsdElement.qualified`). Optional elements (which include SDC4's governance slots:
workflow, subject/provider, protocol, acs, Audit, attestation) are included so the instance
exercises the full governance path. Instance "size" controls how many optional and repeated
elements are emitted.

Validation runs offline via the OASIS catalog (see sdc_catalog.py). Output is committed as
benchmark fixtures so the repo is a standalone clone-and-run resource.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sdc_catalog import load_catalog  # noqa: E402
from sdcvalidator import XMLSchema11  # noqa: E402
from cuid2 import cuid_wrapper  # noqa: E402

_cuid = cuid_wrapper()

SIZE_OPTIONAL = {"small": False, "medium": True, "large": True}
SIZE_REPEATS = {"small": 1, "medium": 1, "large": 3}


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _is_group(particle) -> bool:
    return hasattr(particle, "model") and not hasattr(particle, "type")


def gen_value(t, fixed=None) -> str:
    """A schema-valid text value for a simple-typed leaf."""
    if fixed is not None:
        return _esc(fixed)
    enum = getattr(t, "enumeration", None)
    if enum:
        return _esc(str(enum[0]))
    prim = getattr(t, "primitive_type", None)
    pn = (getattr(prim, "local_name", None) or getattr(t, "local_name", "") or "").lower()
    if "datetime" in pn:
        return "2026-01-01T00:00:00Z"
    if pn == "date":
        return "2026-01-01"
    if pn == "time":
        return "00:00:00"
    if pn == "gyear":
        return "2026"
    if pn == "gyearmonth":
        return "2026-01"
    if pn == "gmonth":
        return "--01"
    if pn == "gday":
        return "---01"
    if pn == "gmonthday":
        return "--01-01"
    if "duration" in pn:
        return "P1D"
    if "bool" in pn:
        return "false"
    if "language" in pn:
        return "en-US"
    if "anyuri" in pn or pn == "uri":
        return "https://example.org/x"
    # numerics: python_type distinguishes int (xs:integer's primitive is decimal) from float/Decimal
    pt = getattr(t, "python_type", None)
    if pt is int:
        mv = getattr(t, "min_value", None)
        return str(mv if isinstance(mv, int) else 1)
    if pt is float or any(k in pn for k in ("decimal", "double", "float")):
        return "1.0"
    ml = getattr(t, "min_length", None) or 1
    return "x" * max(int(ml), 1)


SDC4_NS = "https://semanticdatacharter.com/ns/sdc4/"


def tag_of(el) -> str:
    # elementFormDefault is unqualified: global elements and refs to them are sdc4:-qualified;
    # locally-declared children (label, *-value, ordinal, symbol, ...) are unqualified.
    is_ref = getattr(el, "ref", None) is not None
    is_global = el.is_global() if hasattr(el, "is_global") else False
    return f"sdc4:{el.local_name}" if (is_ref or is_global) else el.local_name


def gen_element(el, size: str, depth: int = 0) -> str:
    """Emit XML for one element occurrence (required count, plus optional/repeat by size)."""
    # ExceptionalValue is the Null-Flavor exception slot; we populate real values, never it.
    if el.local_name == "ExceptionalValue":
        return ""
    # Abstract heads (e.g. the ClusterType `Item` substitution-group head) cannot appear in an
    # instance. Their occurrence is optional (0..*) in the generic types we hit, so omitting them
    # is valid; concrete data uses the restricted component types directly.
    if getattr(el, "abstract", False):
        return ""
    out = []
    min_occ = el.min_occurs or 0
    max_occ = el.max_occurs  # None = unbounded
    if min_occ >= 1:
        n = 1
    elif SIZE_OPTIONAL[size]:
        n = 1
    else:
        return ""  # optional, omitted at small size
    if max_occ is None or max_occ > 1:
        n = max(n, SIZE_REPEATS[size]) if (min_occ >= 1 or SIZE_OPTIONAL[size]) else n
        if max_occ is not None:
            n = min(n, max_occ)
    for _ in range(n):
        out.append(_emit_once(el, size, depth))
    return "".join(out)


def _emit_once(el, size: str, depth: int) -> str:
    pad = "  " * (depth + 1)
    tag = tag_of(el)
    t = el.type
    fixed = getattr(el, "fixed", None)
    if t is None or not t.is_complex():
        return f"{pad}<{tag}>{gen_value(t, fixed)}</{tag}>\n"
    inner = gen_group(t.content, size, depth + 1) if getattr(t, "content", None) is not None else ""
    if inner.strip():
        return f"{pad}<{tag}>\n{inner}{pad}</{tag}>\n"
    return f"{pad}<{tag}/>\n"


def gen_group(group, size: str, depth: int) -> str:
    out = []
    model = getattr(group, "model", "sequence")
    particles = list(group)
    if model == "choice" and particles:
        particles = particles[:1]  # one branch satisfies a choice
    for p in particles:
        if _is_group(p):
            out.append(gen_group(p, size, depth))
        else:
            out.append(gen_element(p, size, depth))
    return "".join(out)


def root_element(schema):
    for e in schema.elements.values():
        if e.local_name.startswith("dm-"):
            return e
    raise SystemExit("no dm-* root element found")


def generate(schema, size: str) -> str:
    r = root_element(schema)
    inner = gen_group(r.type.content, size, 1)
    # stamp a fresh instance id (overwrite the generic placeholder value if present)
    iid = _cuid()
    inner = inner.replace("<instance_id>x</instance_id>", f"<instance_id>{iid}</instance_id>", 1)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<sdc4:{r.local_name} xmlns:sdc4="https://semanticdatacharter.com/ns/sdc4/"\n'
        '  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        f"{inner}"
        f"</sdc4:{r.local_name}>\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("xsd", help="path to a vendored model schema")
    ap.add_argument("--size", choices=list(SIZE_OPTIONAL), default="medium")
    ap.add_argument("--out", default=None, help="write the instance here")
    ap.add_argument("--catalog", default=str(Path(__file__).parent / "catalog.xml"))
    args = ap.parse_args()

    mapper = load_catalog(args.catalog)
    schema = XMLSchema11(args.xsd, uri_mapper=mapper, validation="lax")
    xml = generate(schema, args.size)

    errors = list(schema.iter_errors(xml))
    print(f"{args.xsd} [{args.size}]: {len(xml)} bytes, {len(errors)} errors")
    seen = {}
    for e in errors:
        r = getattr(e, "reason", str(e)).split("\n")[0][:100]
        seen[r] = seen.get(r, 0) + 1
    for r, c in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  x{c}: {r}")
    if args.out:
        Path(args.out).write_text(xml, encoding="utf-8")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
