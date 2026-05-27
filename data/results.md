# Substrate Economics - SDC CPU Benchmark Results

Generated 2026-05-27T23:39:17.604999+00:00 | N=1000/class | Python 3.13.5 | Linux-6.17.0-29-generic-x86_64-with-glibc2.39
Versions: sdcvalidator 4.0.1, sdcgovernance 4.0.4, pyshacl 0.30.0
Cost bases: cloud $0.048/vCPU-hr, on-prem $0.014/vCPU-hr (amortized).

## Per-decision CPU and cost (full-stack = BIS + CSAS + ACPS)

| Model | Size | bytes | BIS ms | CSAS ms | ACPS ms | Full-stack ms | $/dec (cloud) | $/dec (on-prem) | verdict variance |
|---|---|--:|--:|--:|--:|--:|--:|--:|:--|
| Employment-Record | small | 511 | 14.177 | 0.944 | 0.770 | 15.891 | $2.12e-07 | $6.18e-08 | 0 (zero, by construction) |
| Employment-Record | medium | 8638 | 16.265 | 4.655 | 2.700 | 23.620 | $3.15e-07 | $9.19e-08 | 0 (zero, by construction) |
| Employment-Record | large | 16414 | 17.946 | 8.251 | 4.493 | 30.690 | $4.09e-07 | $1.19e-07 | 0 (zero, by construction) |
| Healthcare-Record | small | 508 | 31.855 | 1.548 | 1.359 | 34.762 | $4.63e-07 | $1.35e-07 | 0 (zero, by construction) |
| Healthcare-Record | medium | 8635 | 33.737 | 5.241 | 3.247 | 42.225 | $5.63e-07 | $1.64e-07 | 0 (zero, by construction) |
| Healthcare-Record | large | 16411 | 34.939 | 8.791 | 5.071 | 48.801 | $6.51e-07 | $1.90e-07 | 0 (zero, by construction) |

## Annual cost projection (Healthcare-Record, medium; full-stack)

| Scale point | decisions/day | SDC annual (cloud) | SDC annual (on-prem) |
|---|--:|--:|--:|
| Pilot | 2,400 | $0.49 | $0.14 |
| Department | 10,000 | $2.05 | $0.60 |
| Hospital | 100,000 | $20.55 | $5.99 |
| Health System | 1,000,000 | $205.49 | $59.94 |
| Sovereign Large | 10,000,000 | $2,054.93 | $599.35 |

Compare the inference side (Paper 50 section 5): $0.43-$9.80 per full-stack decision, average 1.36x re-run multiplier for a defensible repeatable verdict. The deterministic substrate side has zero verdict variance by construction (multiplier 1.0).
