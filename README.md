# Substrate Economics

**The token-cost asymmetry between deterministic and inference-based governance.**

A joint research paper and reproducibility bundle. Runtime governance validation costs differ by orders of magnitude depending on whether the validation is **deterministic (CPU-bound)** or **inference-based (LLM-bound)**, and the gap is structural, not incremental, at deployment scale. A separate and harder-to-dispute result: deterministic validation has **zero verdict variance by construction**, which satisfies the "defensible repeatable verdict" requirement of regulatory frameworks (EU MDR, Swedish NMI, EU AI Act) at no re-run cost, while inference-based evaluation incurs a measured re-run tax.

**Scope discipline:** this concerns the **runtime** governance layer only (structural validation, policy evaluation, reasoning, receipt verification). Design-time tooling that uses LLMs is a different layer with different economics and is explicitly out of scope.

## Authorship

- **Substrate side:** Axius SDC, Inc. — deterministic CPU-bound governance (`sdcvalidator`, `sdcgovernance`, SHACL/OWL reasoning, hash-chained receipts).
- **Measurement side:** MTCP Research Programme — inference-side cost and variance data from a large multi-model evaluation corpus.

Lead author: Timothy W. Cook (Axius SDC). Full author list, CRediT roles, and contributor ORCIDs are recorded in `/paper`.

## Repository structure

```
/paper        The manuscript. Licensed CC BY 4.0 (see paper/LICENSE).
/benchmarks   The CPU benchmark harness and METHODOLOGY.md. Licensed Apache-2.0.
/data         Raw timing data, environment manifest, and cost-basis sources —
              the reproducibility bundle published alongside the DOI.
```

## Status

The substrate-side benchmark is built and run: fixtures (ten CordovaOS models, offline via an OASIS catalog), a schema-driven valid-instance generator, and the BIS/CSAS/ACPS CPU harness. Results are in `data/` and reproduce offline from a clone (`pip install -r requirements.txt && python benchmarks/run_benchmark.py`). The measurement (inference) side is supplied by the MTCP side; see `benchmarks/README.md` for the reproduction guide and `benchmarks/METHODOLOGY.md` for the design.

## Reproducibility and citation

The benchmark harness, raw timing data, and a pinned environment manifest are published here so the result is independently checkable. On publication, a release is tagged and a versioned DOI is minted (Zenodo's GitHub integration mints a DOI per release). This repository is private during development and made public at publication.

## Licensing

- Code and benchmark harness: **Apache-2.0** (`LICENSE`), consistent with the SDC libraries.
- The manuscript in `/paper`: **CC BY 4.0** (`paper/LICENSE`).
