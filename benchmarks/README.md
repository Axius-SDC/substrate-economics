# Benchmarks

The substrate-side CPU benchmark for *Substrate Economics* (Paper 50). It measures the
per-decision process-CPU cost of SDC runtime-governance operations and projects it across
five deployment scale points, alongside a zero-verdict-variance demonstration. Together with
the inference-side data in Paper 50, this produces the comparison the paper makes.

Everything runs **fully offline from a clone** — pure Python, no triplestore, no GPU, no
Docker, no network.

## Reproduce

```bash
pip install -r ../requirements.txt
python run_benchmark.py            # add --n 1000 for the published settings (default 400)
```

This writes `../data/results.json` (full data + environment manifest) and
`../data/results.md` (the summary tables). Offline schema resolution is handled by the
committed OASIS `catalog.xml` + collocated SDCRM (see below), so no network is touched.

## What it measures

Three per-decision classes, mirroring Paper 50's runtime set, each composed of the SDC
operations that render the deterministic equivalent:

| Class | What it evaluates | SDC operations timed |
|---|---|---|
| **BIS** | constraint persistence, single system | structural validation + SHACL constraint reasoning + receipt |
| **CSAS** | constraint persistence at a coordination boundary | validation (source) + XACML governance advisory + validation (boundary) + receipt |
| **ACPS** | constraint persistence under adversarial pressure | validation + XACML governance advisory + receipt (verdict invariant) |

Full-stack decision = BIS + CSAS + ACPS, matching Paper 50's 4,750-token full-stack decision.
Metric is **process CPU time** per decision (`time.process_time`), N≥1000, steady state, on
valid governed instances at small/medium/large sizes. The schema is compiled once per model
(amortized). Verdict variance is demonstrated by hashing the validation+governance outcome
across repeated runs of identical input.

## Result (current run)

Full-stack per decision lands at tens of milliseconds of CPU — fractions of a millionth of a
dollar — against the inference side's $0.43–$9.80 per decision: a 6–7 order-of-magnitude gap,
with **zero verdict variance by construction** (multiplier 1.0) versus the inference side's
1.36× average re-run tax. See `../data/results.md` for the numbers and `../data/results.json`
for the full breakdown and manifest.

## Cost-basis assumptions

Per-decision dollars = CPU-seconds × $/vCPU-second, reported on two bases (edit the constants
at the top of `run_benchmark.py`):

- **Cloud** — `CLOUD_VCPU_HR = $0.048/vCPU-hour`, a representative general-purpose cloud rate.
- **On-prem (amortized)** — `ONPREM_VCPU_HR = $0.014/vCPU-hour`, a commodity server amortized
  over useful life at moderate utilization; this is the sovereign-relevant lower bound.

The per-decision **order of magnitude is robust** to these rates: even a 10× swing leaves the
gap at 5–6 orders of magnitude. Annual totals are presented as projections with the
decisions/day denominator exposed, not as a headline.

## Layout

```
sdcrm/sdc4/schemas/   complete SDCRM reference model (collocated for offline resolution)
catalog.xml           OASIS catalog mapping SDC4 URIs to sdcrm/ (so model schemas stay byte-identical)
sdc_catalog.py        loads catalog.xml into a uri_mapper for sdcvalidator
fixtures/<Model>/      the ten CordovaOS government models (byte-identical), + SHACL .ttl, JSON-LD
instances/<Model>/     generated valid, governed instances (small/medium/large)
prepare_fixtures.py   (maintainer) vendors the models + catalog from CordovaOS + SDCRM
generate_instances.py (maintainer) schema-driven valid-instance generator
run_benchmark.py      the benchmark
METHODOLOGY.md        full benchmark design
PRD-benchmark-dataset.md  dataset/fixtures specification
```

`prepare_fixtures.py` and `generate_instances.py` regenerate the committed fixtures; a cloner
does not need them — the fixtures and instances are committed so `run_benchmark.py` runs
straight from a clone.

## Scope and honesty notes

- **Runtime only.** This concerns the runtime governance layer (deterministic, CPU-bound).
  Design-time SDC tooling that uses LLMs is a different layer with different economics and is
  out of scope.
- **SHACL reasons over the model's constraint graph** (shapes), so the BIS component scales
  by *model* complexity, not by instance size; CSAS/ACPS scale with instance size. Read the
  BIS figure as "constraint reasoning over the model's shapes."
- **Representative set.** Two models (Employment-Record, Healthcare-Record) span simple-to-
  complex. The generator is schema-driven and extends to all ten.
- **Governance population.** Instances carry the full governance *schema* (all dimensions
  present and advisory-evaluated); deep per-instance governance state (workflow chains, audit
  histories) is a realism layer, not a correctness condition for the cost.
