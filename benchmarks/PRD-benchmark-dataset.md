# PRD — Benchmark Dataset & Fixtures

**Committed specification.** One version, built in a single pass and shipped. Pairs with `METHODOLOGY.md` and produces the data that fills the SDC placeholder in Ahmad's Paper 50, §5.

**Status:** locked, 2026-05-27.

---

## 1. Goal

Produce the SDC-side per-decision CPU cost and the zero-variance demonstration that fill the placeholder in *Substrate Economics* (Paper 50) §5, at the **same five scale points**, for the **same per-decision classes**, computed the **same way** as the inference side, so the comparison is apples-to-apples. We build all fixtures, run all classes, compute the numbers, and ship in one pass. No phases, no v2.

## 2. Classes to parallel (locked from Paper 50)

Paper 50 scopes per-decision runtime inference to exactly three MTCP classes. The SDC side measures the deterministic equivalent of each. **Full-stack = all three (BIS + CSAS + ACPS); that is the comparable unit**, matching Paper 50's 4,750-token full-stack decision at $0.43–$9.80.

| MTCP class | What it evaluates | SDC-side equivalent (CPU-bound) | CordovaOS scenario |
|---|---|---|---|
| **BIS** | constraint persistence across a multi-turn interaction (single system) | `sdcvalidator` structural validation + SHACL/OWL constraint reasoning + receipt write | re-validate a Healthcare-Record instance still holds its declared constraints |
| **CSAS** | constraint persistence at the coordination boundary between two systems | `sdcvalidator` + `sdcgovernance` XACML (cross-domain authorization) + receipt, across two registries | a record crossing Healthcare-Record → Tax-and-Revenue-Record |
| **ACPS** | constraint persistence under adversarial pressure | the same validation pipeline run against an adversarially-perturbed payload; the deterministic verdict is invariant | the same constraint check on an adversarially-framed payload; verdict unchanged, cost is the validation cost |

ACPS is where the architecture shows: the inference side pays 2,200 tokens plus variance per adversarial evaluation; the deterministic side pays the validation cost and returns the same verdict regardless of framing.

**Out of scope (exactly as Paper 50 scopes them):** the constitutional-layer frameworks (COS, LRP, GRC) are design-time; DRA and TDS are periodic; BEC hash-chain is negligible; the Admissibility Gate is a threshold lookup. Do not measure SDC operations that have no per-decision MTCP counterpart (schema-only, authority-only, provenance-only, jurisdiction-only) for the headline comparison; the comparable unit is the BIS + CSAS + ACPS full stack.

## 3. Scale points (locked from Paper 50)

Per-decision → daily → annual at each, same rollup as the inference side:

| Scale point | Decisions/day |
|---|---|
| Pilot | 2,400 |
| Department | 10,000 |
| Hospital | 100,000 |
| Health System | 1,000,000 |
| Sovereign Large | 10,000,000 |

## 4. Fixtures (single committed build)

- **Models.** Copy the ten CordovaOS registries (Business, Civil, Education, Employment, Healthcare, Law-Enforcement, Maritime-Port-Authority, Property, Tax-and-Revenue, Vital-Statistics) and compose the @ProvGov families into them. **Mint new CUIDs for the composed model schemas only** — each is a new artifact because the ProvGov composition changes the schema. **Reuse every constituent component CUID unchanged** (CordovaOS and ProvGov alike); reuse-by-reference preserves identity, so do not edit components in situ.
- **Track the modifications.** Record which ProvGov families are composed into which model. The composed schemas differ from the originals, and that delta is what drives the new templates below, so it must be documented.
- **XML templates.** Because the composed models are new schemas with new CUIDs, generate **new SDC4 XML template/instance files pointing to the new composed-model CUIDs**. The existing CordovaOS templates point to the pre-ProvGov models and cannot be reused as-is.
- **Data.** Reuse the existing CordovaOS instance data directly. It is **all synthetic (no PII)**, so it ships as-is into the new templates. No fresh data generation required.
- **Policy sets.** Representative XACML policy sets for the CSAS cross-domain authorization decisions, at a small and a larger complexity, so cost-vs-policy-complexity is a measured curve.
- **Provenance chains.** Receipts at representative chain depth so receipt write/verify cost is captured.

## 5. Harness & infrastructure

Exercise `sdcvalidator` + `sdcgovernance` (XACML + Receipt corpus) + the runtime reasoner (Apache Jena / Fuseki) + receipt storage **directly** via the harness against the fixtures. No full Django app, no full DB restore. Extract the @ProvGov family definitions from the SDCStudio backup `sdcstudio_cloudsql_20260527_171128.sql.gz`. Isolate process CPU time per decision so the number is not contaminated by app-server, DB-I/O, or network overhead. Pin every version in the manifest (`METHODOLOGY.md` §7).

## 6. Cost model & output

- Per-decision SDC cost = CPU-seconds/decision × $/vCPU-second + receipt storage, on **two bases** (cloud reference rate and on-prem amortized), variance multiplier = **1.0** by construction.
- **Fill Paper 50 §5:** the deterministic-side per-decision, daily, and annual cost at all five scale points, presented as transparent ranges with assumptions exposed, directly beside the inference-side figures.
- **Lead result:** the zero-variance demonstration — verdict hash identical across all N runs of identical input — paired against the inference side's 1.36x average / 3–5x worst-case re-run multiplier.

## 7. Reproducibility & IP

Commit the fixture set (composed models + new XML templates + the reused synthetic CordovaOS data + policy sets), the harness, and the raw timing data, so the result is independently checkable. All generated artifacts are Apache-2.0; CordovaOS is already public. **Confirm before publishing** that only generated model/component/template/data/policy artifacts go in, and that no SDCStudio publisher/generator internals leak into the fixtures.
