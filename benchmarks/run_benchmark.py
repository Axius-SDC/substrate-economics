#!/usr/bin/env python3
"""
Substrate-side CPU benchmark for *Substrate Economics* (Paper 50, section 5).

Measures the per-decision process-CPU cost of the SDC runtime-governance operations that
render the deterministic equivalent of MTCP's three per-decision classes, on valid governed
instances of the CordovaOS models, and projects the cost across the same five scale points as
the inference side. Also demonstrates zero verdict variance by construction.

Decision classes (SDC-side composition; see PRD-benchmark-dataset.md / METHODOLOGY.md):
  BIS  = structural validation + SHACL constraint reasoning + receipt
  CSAS = structural validation (source) + XACML governance advisory + structural validation
         (boundary) + receipt
  ACPS = structural validation + XACML governance advisory + receipt  (verdict invariant under
         adversarial framing -> the zero-variance result)
Full-stack decision = BIS + CSAS + ACPS, matching Paper 50's 4,750-token full-stack decision.

Runs fully offline against the committed fixtures via the OASIS catalog. No network, no
triplestore, no GPU.  Usage:  python benchmarks/run_benchmark.py [--n 400]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import rdflib

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from sdc_catalog import load_catalog  # noqa: E402
from sdcvalidator import XMLSchema11  # noqa: E402
from sdcgovernance import validate_governance  # noqa: E402
from sdcgovernance.shacl_runtime import validate_shacl  # noqa: E402
from sdcgovernance.receipts import ReceiptChain, Decision  # noqa: E402

DATA = HERE.parent / "data"

# --- Cost bases (documented parameters; the per-decision order of magnitude is robust to these). ---
CLOUD_VCPU_HR = 0.048    # USD/vCPU-hour, representative general-purpose cloud rate
ONPREM_VCPU_HR = 0.014   # USD/vCPU-hour, commodity server amortized (see README for assumptions)

SCALE_POINTS = [("Pilot", 2_400), ("Department", 10_000), ("Hospital", 100_000),
                ("Health System", 1_000_000), ("Sovereign Large", 10_000_000)]

MODELS = {
    "Employment-Record": "dm-pm5cks82lnrvyna1xbwpfxic",
    "Healthcare-Record": "dm-ftluo2nybgxmn7mawttoos20",
}
SIZES = ["small", "medium", "large"]


def usd_per_cpu_sec(rate_hr: float) -> float:
    return rate_hr / 3600.0


def stats_ms(samples_s: list[float]) -> dict:
    ms = sorted(s * 1000 for s in samples_s)
    n = len(ms)
    return {
        "mean_ms": round(statistics.fmean(ms), 5),
        "median_ms": round(statistics.median(ms), 5),
        "p95_ms": round(ms[min(int(0.95 * n), n - 1)], 5),
        "p99_ms": round(ms[min(int(0.99 * n), n - 1)], 5),
        "stdev_ms": round(statistics.pstdev(ms), 5),
    }


def time_decision(ops, n: int, warmup: int = 20) -> list[float]:
    for _ in range(warmup):
        for o in ops:
            o()
    samples = []
    for _ in range(n):
        t = time.process_time()
        for o in ops:
            o()
        samples.append(time.process_time() - t)
    return samples


def bench_model(name: str, cuid: str, mapper, n: int) -> dict:
    base = HERE / "fixtures" / name / cuid
    xsd = str(base.with_suffix(".xsd"))
    t0 = time.process_time()
    schema = XMLSchema11(xsd, uri_mapper=mapper, validation="lax")
    compile_ms = (time.process_time() - t0) * 1000
    # Shapes + constraint graph parsed once (cached, as in production); SHACL reasoning is timed.
    g_shapes = rdflib.Graph().parse(str(base) + "_shacl.ttl", format="turtle")
    g_data = rdflib.Graph().parse(str(base) + ".jsonld", format="json-ld")

    result = {"compile_ms_one_time": round(compile_ms, 3), "sizes": {}}
    for size in SIZES:
        inst = HERE / "instances" / name / f"{cuid}-{size}.xml"
        xml = inst.read_text()
        chain = ReceiptChain()

        op_validate = lambda: list(schema.iter_errors(xml))  # noqa: E731
        op_shacl = lambda: validate_shacl(data_graph=g_data, shapes_graph=g_shapes)  # noqa: E731
        op_gov = lambda: validate_governance(xsd, str(inst))  # noqa: E731
        op_receipt = lambda: chain.append(decision=Decision.PERMIT, reasoning="d",  # noqa: E731
                                          instance_id="i", instance_version="1")

        classes = {
            "BIS": [op_validate, op_shacl, op_receipt],
            "CSAS": [op_validate, op_gov, op_validate, op_receipt],
            "ACPS": [op_validate, op_gov, op_receipt],
        }
        size_res = {}
        for cls, ops in classes.items():
            size_res[cls] = stats_ms(time_decision(ops, n))

        # zero-variance demonstration: identical input -> identical verdict, every time
        verdicts = set()
        for _ in range(50):
            errs = op_validate()
            gov = op_gov()
            verdicts.add(hashlib.sha256(
                f"{len(errs)}|{getattr(gov, 'decision', None)}".encode()).hexdigest())
        full_stack = sum(size_res[c]["mean_ms"] for c in ("BIS", "CSAS", "ACPS"))
        size_res["full_stack_mean_ms"] = round(full_stack, 5)
        size_res["distinct_verdicts_over_50_runs"] = len(verdicts)
        size_res["zero_variance"] = (len(verdicts) == 1)
        size_res["instance_bytes"] = len(xml.encode())
        result["sizes"][size] = size_res
    return result


def cost_table(full_stack_ms: float) -> dict:
    cpu_s = full_stack_ms / 1000.0
    out = {"cpu_seconds_per_decision": round(cpu_s, 8),
           "usd_per_decision_cloud": cpu_s * usd_per_cpu_sec(CLOUD_VCPU_HR),
           "usd_per_decision_onprem": cpu_s * usd_per_cpu_sec(ONPREM_VCPU_HR),
           "variance_multiplier": 1.0, "scale_points": {}}
    for label, per_day in SCALE_POINTS:
        out["scale_points"][label] = {
            "decisions_per_day": per_day,
            "annual_usd_cloud": round(out["usd_per_decision_cloud"] * per_day * 365, 2),
            "annual_usd_onprem": round(out["usd_per_decision_onprem"] * per_day * 365, 2),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=400, help="iterations per decision class")
    args = ap.parse_args()
    DATA.mkdir(exist_ok=True)
    mapper = load_catalog(HERE / "catalog.xml")

    import sdcvalidator
    import sdcgovernance
    import pyshacl
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "iterations_per_class": args.n,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "versions": {
            "sdcvalidator": getattr(sdcvalidator, "__version__", "?"),
            "sdcgovernance": getattr(sdcgovernance, "__version__", "?"),
            "pyshacl": getattr(pyshacl, "__version__", "?"),
            "rdflib": rdflib.__version__,
        },
        "cost_bases": {"cloud_vcpu_hr": CLOUD_VCPU_HR, "onprem_vcpu_hr": ONPREM_VCPU_HR},
    }

    results = {"manifest": manifest, "models": {}}
    for name, cuid in MODELS.items():
        print(f"benchmarking {name} ...", flush=True)
        mr = bench_model(name, cuid, mapper, args.n)
        for size, sr in mr["sizes"].items():
            sr["cost"] = cost_table(sr["full_stack_mean_ms"])
        results["models"][name] = mr

    (DATA / "results.json").write_text(json.dumps(results, indent=2))
    write_markdown(results)
    print(f"\nwrote {DATA/'results.json'} and {DATA/'results.md'}")


def write_markdown(results: dict) -> None:
    m = results["manifest"]
    lines = [
        "# Substrate Economics - SDC CPU Benchmark Results",
        "",
        f"Generated {m['generated_utc']} | N={m['iterations_per_class']}/class | "
        f"Python {m['python']} | {m['platform']}",
        f"Versions: sdcvalidator {m['versions']['sdcvalidator']}, "
        f"sdcgovernance {m['versions']['sdcgovernance']}, pyshacl {m['versions']['pyshacl']}",
        f"Cost bases: cloud ${m['cost_bases']['cloud_vcpu_hr']}/vCPU-hr, "
        f"on-prem ${m['cost_bases']['onprem_vcpu_hr']}/vCPU-hr (amortized).",
        "",
        "## Per-decision CPU and cost (full-stack = BIS + CSAS + ACPS)",
        "",
        "| Model | Size | bytes | BIS ms | CSAS ms | ACPS ms | Full-stack ms | "
        "$/dec (cloud) | $/dec (on-prem) | verdict variance |",
        "|---|---|--:|--:|--:|--:|--:|--:|--:|:--|",
    ]
    for name, mr in results["models"].items():
        for size, sr in mr["sizes"].items():
            c = sr["cost"]
            zv = "0 (zero, by construction)" if sr["zero_variance"] else \
                 f"{sr['distinct_verdicts_over_50_runs']} distinct"
            lines.append(
                f"| {name} | {size} | {sr['instance_bytes']} | {sr['BIS']['mean_ms']:.3f} | "
                f"{sr['CSAS']['mean_ms']:.3f} | {sr['ACPS']['mean_ms']:.3f} | "
                f"{sr['full_stack_mean_ms']:.3f} | ${c['usd_per_decision_cloud']:.2e} | "
                f"${c['usd_per_decision_onprem']:.2e} | {zv} |")
    # one representative scale-point projection
    lines += ["", "## Annual cost projection (Healthcare-Record, medium; full-stack)", "",
              "| Scale point | decisions/day | SDC annual (cloud) | SDC annual (on-prem) |",
              "|---|--:|--:|--:|"]
    sp = results["models"]["Healthcare-Record"]["sizes"]["medium"]["cost"]["scale_points"]
    for label, _ in SCALE_POINTS:
        d = sp[label]
        lines.append(f"| {label} | {d['decisions_per_day']:,} | "
                     f"${d['annual_usd_cloud']:,.2f} | ${d['annual_usd_onprem']:,.2f} |")
    lines += ["",
              "Compare the inference side (Paper 50 section 5): $0.43-$9.80 per full-stack "
              "decision, average 1.36x re-run multiplier for a defensible repeatable verdict. "
              "The deterministic substrate side has zero verdict variance by construction "
              "(multiplier 1.0).", ""]
    (DATA / "results.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
