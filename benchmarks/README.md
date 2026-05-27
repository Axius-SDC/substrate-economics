# Benchmarks

The substrate-side CPU benchmark harness and its methodology.

- **`METHODOLOGY.md`** — the full benchmark design: comparability principle, decision classes, scale points, what to measure and how, the cost model, the verdict-variance demonstration, and the reproducibility manifest. Read this before building or running the harness.
- The harness code lands here as it is built. Licensed **Apache-2.0** (repository-root `LICENSE`).
- Running the harness produces the raw timing data and manifest written to `/data`.

Design goal in one line: produce SDC-side cost-per-decision, latency, and verdict-variance numbers that compose **directly** with the MTCP inference-side numbers, so the comparison is like-for-like and survives a hostile read.
