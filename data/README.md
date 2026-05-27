# Data

The reproducibility bundle, published alongside the DOI.

Contents (produced by running the harness in `/benchmarks`):

- **Raw timing data** — per-decision process-CPU time, wall-clock latency, peak memory, receipt bytes, and verdict hashes, across decision classes, payload/policy sizes, and stack profiles.
- **Environment manifest** — hardware, OS/kernel, language version, and pinned versions of every measured component, so the numbers are reproducible.
- **Cost-basis sources** — the cited cloud rate card and the on-prem amortization assumptions used to translate CPU-seconds and storage into cost-per-decision.

Raw data is committed so the published result is independently checkable.
