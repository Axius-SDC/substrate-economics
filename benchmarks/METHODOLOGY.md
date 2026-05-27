# CPU Benchmark Methodology — Substrate Side

**Purpose:** produce SDC-side cost-per-decision, latency, and verdict-variance numbers that compose **directly** with the MTCP inference-side numbers, so the two halves form a like-for-like comparison.

---

## 1. The comparability principle (read this first)

The unit of comparison is **one runtime governance decision.** Every choice below exists to make the SDC number and the MTCP number measure the *same decision, at the same scale, on the same cost basis*, so a hostile reviewer cannot dismiss the comparison as apples-to-oranges.

Three things must match the inference side exactly:
1. **The decision classes** measured (Section 3).
2. **The scale points** the per-decision cost is projected across (Section 4).
3. **The cost-rollup formula:** per-decision cost → daily total → annual total, with the same denominators and the same variance treatment (Section 6).

Scope discipline: this is the **runtime** governance layer only. None of the measured components call an LLM. Design-time tooling that uses LLMs is a different layer with different economics and is **out of scope**; state this explicitly in the paper's methodology section.

## 2. What runs on the substrate side (components to instrument)

All deterministic, all CPU-bound:
- **`sdcvalidator`** — structural validation against SDCRM-derived schemas (XSD restriction lattice).
- **`sdcgovernance`** — XACML 3.0 PERMIT/DENY authorization + hash-chained Receipt corpus.
- **SHACL / OWL reasoning** at runtime via `pyshacl` + `rdflib` (pure Python, in-process; no triplestore, no Jena/Fuseki/GraphDB).
- **Receipt corpus** hash-chain append and verify.

Pin and record exact versions of every component in the environment manifest (Section 7). Reproducibility is the credibility mechanism; an unpinned benchmark is not checkable evidence.

## 3. Decision classes (locked from Paper 50: BIS, CSAS, ACPS)

The measurement side's per-decision runtime classes are exactly three. The SDC side measures the deterministic equivalent of each. **Full-stack = all three (BIS + CSAS + ACPS); that is the comparable unit**, matching Paper 50's 4,750-token full-stack decision at $0.43–$9.80.

| MTCP class | What it evaluates | SDC-side equivalent (CPU-bound) |
|---|---|---|
| **BIS** | constraint persistence across a multi-turn interaction (single system) | `sdcvalidator` structural validation + SHACL/OWL constraint reasoning + receipt write |
| **CSAS** | constraint persistence at the coordination boundary between two systems | `sdcvalidator` + `sdcgovernance` XACML (cross-domain authorization) + receipt, across two registries |
| **ACPS** | constraint persistence under adversarial pressure | the same validation pipeline against an adversarially-perturbed payload; the deterministic verdict is invariant, so the cost is the validation cost |

Out of scope, exactly as Paper 50 scopes them: the constitutional-layer frameworks (COS, LRP, GRC) are design-time; DRA and TDS are periodic; BEC hash-chain is negligible; the Admissibility Gate is a threshold lookup. Do not measure SDC operations with no per-decision MTCP counterpart for the headline comparison. Concrete CordovaOS scenarios for each class are in `PRD-benchmark-dataset.md` §2.

## 4. Scale points

| Scale point | Decisions/day | Anchor |
|---|---|---|
| Pilot | ~2,400 (100/hr) | single user, exploratory |
| Department | ~10,000 | one clinical specialty / one business unit |
| Hospital | ~100,000 | one hospital affiliate / mid-sized regional bank |
| Health-system / national | ~1,000,000 | regional health system, NHS-trust class |
| Sovereign-large | ~10,000,000+ | sovereign program / large federal program |

The **decisions-per-day denominator is the single most contestable number** ("is every interaction a full governance decision?"). Treat it as an exposed parameter, not a buried assumption. Present annual totals as transparent ranges driven by this parameter.

## 5. What to measure, and how (the harness)

For each decision class, run **N ≥ 1,000** iterations at steady state (discard warm-up runs) over a representative spread of inputs, and capture:

**Cost-relevant primary metric:**
- **Process CPU time per decision** (the cost number): use `time.process_time()` or `resource.getrusage(RUSAGE_SELF)` / `psutil` per-process CPU, **not** wall-clock, for the dollar figure. CPU-seconds is what maps to a vCPU price.

**Latency (real-time relevance):**
- **Wall-clock per decision** via `time.perf_counter()`. Report mean, median, p95, p99.

**Footprint:**
- **Peak memory per decision** (RSS delta or `tracemalloc` peak).
- **Receipt bytes** per decision (actual serialized + signed receipt size) and **hash-chain verify cost as a function of chain depth** (measure at several depths; provenance cost grows with chain length).

**Throughput (grounds the scale-point extrapolation):**
- **Sustained decisions/second/core** under load, so daily totals derive from measured throughput × cores × utilization rather than a hand-wave. This supports "a single commodity server clears N decisions/day at $X."

**Verdict variance (the gem — Section 8):**
- Hash the verdict output across all N runs of each identical input. Assert the hash is **identical across all N** (zero variance, by construction). Capture and report this explicitly.

Statistics per class: mean, median, p95, p99, and **standard deviation** of CPU-ms. The small standard deviation is itself the contrast to inference-side variance.

**Environment controls:** single-tenant machine, no competing load; CPU governor set to `performance` (or document the policy); record whether turbo/boost is on; repeat the full suite to confirm stability.

**Runtime:** pure Python (`sdcvalidator`, `sdcgovernance`, `pyshacl`, `rdflib`) — no triplestore, no GPU, no Docker; the benchmark runs in-process and offline. Vary **instance size** (small/medium/large) and, where it matters, **policy/constraint-set size**; report the curve, not a single point.

## 6. Cost model (mirror the inference side exactly)

Inference side: `$/decision = (input_tokens + output_tokens) × $/token`, per provider tier, × variance re-run multiplier.

SDC side, same shape so the halves add up:

```
$/decision (SDC) = (CPU_seconds_per_decision × $/vCPU-second)
                 + (receipt_bytes × $/GB-month ÷ decisions_per_month_amortized)
                 + (memory cost, typically negligible — include for completeness)
                 + (network ≈ 0 when validation is local-to-runtime)
variance multiplier (SDC) = 1.0   # zero re-runs, by construction
```

Report **two cost bases**, both as columns:
- **Cloud reference:** a named provider's general-purpose vCPU-hour ÷ 3600 for `$/vCPU-second`; that provider's storage `$/GB-month`. Cite the rate card.
- **On-prem / sovereign amortized:** server capital cost amortized over useful life ÷ (cores × utilization × seconds). This is the **sovereign-relevant** figure and a likely lower bound; air-gapped deployment is a key audience.

Roll up identically to the inference side: `$/decision → daily (× decisions/day) → annual (× 365)`, at each scale point, annual presented as a range.

## 7. Reproducibility manifest (publish in `/data`)

- Hardware: CPU model, base/boost clock, physical/logical cores, RAM, storage type. A commodity workstation is a reasonable reference; note that a CPU benchmark needs no GPU, which is itself a point worth making.
- OS + kernel, language version, and **pinned versions** of `sdcvalidator`, `sdcgovernance`, `pyshacl`, and `rdflib` (captured automatically into `data/results.json`).
- The **benchmark harness** (committed to `/benchmarks`), the **raw timing data** (CSV/Parquet in `/data`), and the input corpus or its generator.
- Cost-basis sources (the cited cloud rate card; the on-prem amortization assumptions).

## 8. The variance / repeatability result (make it first-class)

The most defensible finding and the **regulatory** argument, so it gets its own result, not a footnote:

- **Demonstrate** zero verdict variance: across all N runs of identical input, the verdict hash is identical. SDC meets "defensible repeatable verdict" (the MDR / Swedish NMI / EU AI Act requirement) **by construction, at no re-run cost.**
- **Contrast** with the measured inference-side variance, where some models require repeated runs to reach a defensible repeatable verdict, carrying a re-run cost multiplier. On the inference side, repeatability is a *purchased* property with a structural tax; on the substrate side it is free.
- Frame this as a lead result alongside the per-decision order-of-magnitude gap. It survives a hostile read because it is an architectural property, not an estimate.

## 9. Framing discipline (rigor as credibility)

- Lead with the **per-decision order-of-magnitude gap** and the **variance/repeatability structure.** Both survive scrutiny.
- Present **annual totals as transparent ranges** with the decisions/day denominator and cost basis exposed. Do **not** lead with an annual headline figure; it is the product of two ceilings × the most contestable denominator, and is the easiest number for a skeptic to attack and thereby discredit the whole paper.
- Report what the data shows, not what the hypothesis wants. If the gap is smaller than expected for some class, say so; an honest, narrower result is more useful than an overclaimed one and protects the credibility of the open evidence.

## 10. Outputs

1. **SDC results table:** per decision class × scale point × stack profile → CPU $/decision (cloud + on-prem), latency (mean/p95/p99), receipt bytes, memory, verdict-variance (= 0).
2. **Joined comparison table:** SDC vs MTCP, per decision class, per scale point — the paper's core exhibit.
3. **Reproducibility bundle:** harness + raw data + manifest, published with the DOI.

---

### Run order
1. Build the fixtures per `PRD-benchmark-dataset.md` (compose ProvGov into copied CordovaOS models, mint composed-model CUIDs only, generate new XML templates, reuse the synthetic data).
2. Build the harness; pin versions; write the manifest.
3. Run all three classes (BIS, CSAS, ACPS) in the pure-Python runtime, N ≥ 1,000, across instance sizes; capture all metrics including verdict hashes.
4. Compute $/decision (both cost bases) and the variance result.
5. Review the order-of-magnitude before drafting conclusions; then write the substrate-side results into Paper 50 §5 and the manuscript, joined with the inference-side numbers.
