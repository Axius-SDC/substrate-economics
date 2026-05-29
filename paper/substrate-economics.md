# Substrate Economics

## The Token-Cost Asymmetry Between Deterministic and Inference-Based Governance

**Timothy W. Cook**, Axius SDC, Inc.

**Ahmad Abby**, MTCP Research Programme

Contact: [contact@axius-sdc.com](mailto:contact@axius-sdc.com) DOI: (on publication) June 2026

---

## Abstract

Runtime governance validation costs differ by orders of magnitude depending on validation type. Deterministic CPU-bound validation and inference-based LLM-bound validation occupy entirely different cost regimes.

This paper quantifies the per-decision cost gap. It uses empirical token consumption data from 183,924 MTCP evaluations and an SDC CPU benchmark. The gap is structural, not incremental. It widens at scale.

A second structural difference is verdict variance. Deterministic substrate validation produces zero verdict variance by construction. It automatically meets MDR and NMI repeatable verdict requirements. Inference-based evaluation has an average re-run multiplier of 1.36x across 35 models. Worst-case multipliers reach 3-5x for high-variance models.

The combined cost-and-variance argument constitutes an economic case for substrate-first governance. This case is independent of architectural and intellectual arguments.

**Keywords:** substrate-first governance; deterministic validation; inference cost; verdict variance; total cost of ownership; regulated AI; sovereign deployment; SHACL; XACML; reproducibility.

## 1\. Introduction

The substrate-first thesis has been argued on two dimensions. Architectural: deterministic validation provides provable correctness. Intellectual: schema-based reasoning formally captures constraint semantics. This paper opens a third dimension. Economics.

The recognition is not new. It surfaced during SDCStudio rate-setting. Most validation cost was CPU time, not inference. What is new is the scale that makes it matter.

Governance validation costs are typically excluded from total cost-of-ownership analyses of AI deployment. Those analyses tend to count model inference and integration costs, while treating per-decision governance as fixed or negligible overhead. At a regulated scale, that assumption does not hold, and the omission is the gap this paper addresses.

A large regional health system can run on the order of 8 million doctor visits and 490,000 emergency visits annually, with several hospitals operating executive-approved AI-assisted decision support. EU MDR and Swedish NMI impose per-decision compliance overhead.

At that volume, the per-decision cost difference compounds. It compounds into a materially different total cost of ownership. The argument has moved from the abstract to the buyer's room.

This paper presents the inference-side cost data from MTCP empirical measurements alongside the SDC CPU benchmark data. The comparison is the argument.

## 2\. Methods

### 2.1 Scope: runtime versus design-time

The cost argument applies only to the runtime governance layer. Not all governance operations are per-decision. The distinction matters.

Three MTCP evaluation types constitute per-decision runtime inference. BIS measures constraint persistence across a full multi-turn interaction. CSAS measures constraint persistence at coordination boundaries between two systems. ACPS measures constraint persistence under adversarial pressure.

All other MTCP layers are design-time, periodic, or of negligible cost. Constitutional layer frameworks (COS, LRP, GRC) are design-time definitions established once. They are not per-decision. DRA and TDS are periodic assessments. They run at scheduled intervals, not per decision. BEC hash-chain operations have a negligible CPU cost. The Admissibility Gate is a threshold lookup, not an inference call.

On the SDC side, the runtime layer is deterministic and CPU-bound. The sdcvalidator validates payload structure. The sdcgovernance XACML engine evaluates access policies. SHACL and OWL reasoning validate schema constraints. Receipt corpus hash-chain operations provide tamper evidence. All are CPU-bound at runtime.

The SDC Agents suite uses LLMs at design-time. That is a different layer with different economics. Runtime governance validation is the subject of comparison throughout this paper.

### 2.2 Unit of comparison, decision composition, and scale points

The unit of comparison is one runtime governance decision. Every methodological choice exists to make the substrate figure and the inference figure measure the same decision, at the same scale, on the same cost basis. Hence, the comparison is not dismissible as apples-to-oranges. Three things match across both sides: the decision classes measured, the scale points over which the per-decision cost is projected, and the cost-rollup formula.

A full-stack per-decision evaluation comprises all three runtime classes: BIS, CSAS, and ACPS. The two sides are instrumental in the same composition. On the inference side, each class is an MTCP evaluation. On the substrate side, BIS comprises structural validation, SHACL constraint reasoning, and a hash-chained receipt; CSAS adds an XACML governance advisory across a system boundary; ACPS adds the governance advisory under an adversarial framing.

Per-decision cost is projected across five scale points, identical on both sides:

| Scale point | Decisions/day | Anchor |
| :---- | ----: | :---- |
| Pilot | 2,400 | single user, exploratory |
| Department | 10,000 | one clinical specialty or business unit |
| Hospital | 100,000 | one large hospital or mid-sized regional bank |
| Health System | 1,000,000 | a whole regional health system, NHS-trust class |
| Sovereign Large | 10,000,000 | Gulf sovereign or large federal program |

The decisions-per-day denominator is the single most contestable input. It is treated as an exposed parameter, not a buried assumption: annual totals are presented as transparent ranges driven by it, never as a headline figure. The cost-rollup is identical on both sides: per-decision cost, to daily total (times decisions per day), to annual total (times 365), presented as a range at each scale point.

### 2.3 Inference-side cost estimation

Token consumption per evaluation type is estimated from the standard MTCP protocol structure. Actual token counts are not stored in the evaluation database. Estimates are validated against the probe structure.

The per-class token assumptions are: BIS, 350 input and 500 output tokens, total 850 (a three-turn protocol that delivers the constraint, applies correction, and assesses final compliance); CSAS, 700 input and 1,000 output tokens, total 1,700 (two models each run the full three-turn protocol); ACPS, 1,200 input and 1,000 output tokens, total 2,200 (four adversarial attack types, each requiring structured prompts longer than standard probes). The full-stack composition, therefore, totals 4,750 tokens per decision.

Cost per decision is computed as the sum of input and output tokens, multiplied by the per-token price for a given provider tier, multiplied by any verdict-variance re-run multiplier. Two provider tiers bound the range. The floor uses the cheapest provider, AWS Bedrock Nova Micro, at $0.035 per 1,000 input tokens and $0.14 per 1,000 output tokens. The ceiling uses Nova Pro at $0.80 per 1,000 input tokens and $3.20 per 1,000 output tokens.

### 2.4 Substrate-side CPU benchmark

The SDC runtime-governance operations were benchmarked at the same five scale points with the same per-decision composition, on valid governed instances of the CordovaOS government data models. The components instrumented are all deterministic and CPU-bound: sdcvalidator for structural validation against SDCRM-derived schemas; sdcgovernance (v4.0.1) for XACML 3.0 PERMIT/DENY authorization and the hash-chained Receipt corpus; SHACL and OWL constraint reasoning; and Receipt corpus hash-chain append and verify.

Process CPU time per decision was measured as the cost-relevant metric, at N \= 1,000 iterations per class at steady state, discarding warm-up runs. The benchmark ran fully offline: no triplestore server, no GPU, no network. Inputs spanned a simple model (Employment-Record) and a complex one (Healthcare-Record), each at small, medium, and large instance sizes, so per-decision cost is reported as a function of model and payload complexity rather than as a single point.

The substrate cost model mirrors the inference cost model, so the two halves compose. Per-decision substrate cost is CPU-seconds per decision times the per-vCPU-second rate, plus negligible terms for receipt storage and memory, with network cost approximately zero when validation is local to the runtime. The variance multiplier is 1.0 by construction. Two cost bases are reported in separate columns: a cloud reference rate of $0.048 per vCPU-hour and an amortized on-premises rate of $0.014 per vCPU-hour, the latter being the sovereign-relevant figure and a likely lower bound.

The benchmark, fixtures, raw timing data, and environment manifest are published for independent reproduction (see Data and Code Availability).

### 2.5 Verdict-variance measurement

On the inference side, verdict variance was characterized across 35 models using the MTCP corpus. For each model, verdict outcomes for the same constraint were compared between sampling temperature T=0.0 and T=0.8. The resulting deltas were classified into three bands, and each band was mapped to the number of re-runs required to reach a defensible repeatable verdict: stable (delta below 2 percent), moderate (2 to 10 percent), and high (above 10 percent).

On the substrate side, the verdict output was hashed across all N runs of each identical input, and the hashes were compared for identity. A single distinct hash across all runs demonstrates zero verdict variance by construction.

## 3\. Results

### 3.1 Per-decision cost: inference side

Cost per BIS evaluation ranges from $0.082 (Nova Micro tier) to $1.88 (Nova Pro tier). Cost per full-stack decision ranges from $0.43 (floor) to $9.80 (ceiling).

Cost per million BIS evaluations: $82,250 (floor) to $1,880,000 (ceiling). Cost per million full-stack decisions: $428,750 (floor) to $9,800,000 (ceiling).

These are order-of-magnitude estimates. Volume discounts, reserved capacity, and provider-specific agreements reduce actual costs. The per-decision order-of-magnitude is the primary finding. Annual totals at scale follow as illustrations.

### 3.2 Verdict variance

Deterministic substrate validation produces zero verdict variance by construction. The same payload evaluated twice against the same schema and policy produces identical results. Every time. Without exception. This automatically meets the EU MDR Article 22 and Swedish NMI per-decision defensibility requirements. No re-run cost multiplier applies.

Inference-based evaluation carries measurable verdict variance. The same model evaluated on the same constraint at the same temperature can produce different outcomes across runs. This is intrinsic to probabilistic inference, not an implementation failure.

The MTCP corpus quantifies this variance across 35 models. Twenty-two models produce stable verdicts without re-runs. These are deterministic-equivalent in practice at T=0.0. Their variance between T=0.0 and T=0.8 is below 2 percent.

Eleven models show moderate variance ranging from 2 to 10 percent. These require 1.5 to 2.0 re-runs to achieve a defensible, repeatable verdict. The affected model families include Claude, Qwen, Cohere, GPT-mini, Granite, Nova Pro, Phi, Gemma, Grok, and Llama-8b.

Two models show high variance above 10 percent. These require 3 to 5 re-runs for defensible verdicts. One model shows a 34.9 percent delta between T=0.0 and T=0.8. It requires a 5.0x cost multiplier. Another shows a 17.3 percent delta requiring a 3.0x multiplier.

The average re-run multiplier across all 35 models is 1.36x.

The inference side pays a tax to reach a defensibility standard that the deterministic side meets by construction. Under frameworks that require defensible, repeatable verdicts, this is not a cost-optimization problem. It is a regulatory architecture problem.

The 1.36x average multiplier and 3x to 5x worst-case are structural features of inference-based evaluation. They are not implementation failures. They follow from the probabilistic nature of LLM inference. No amount of engineering eliminates verdict variance from a probabilistic system.

### 3.3 Scale point cost comparison: inference side

Five scale points illustrate the cost of increasing deployment volume. All figures use the full-stack evaluation (BIS, CSAS, and ACPS) at the floor and ceiling provider tiers.

Pilot scale: 2,400 decisions per day. Daily cost: $1,029 (floor) to $23,520 (ceiling). Annual cost: $375,585 (floor) to $8.6 million (ceiling).

Department scale: 10,000 decisions per day. Daily cost: $4,288 (floor) to $98,000 (ceiling). Annual cost: $1.6 million (floor) to $35.8 million (ceiling).

Hospital scale: 100,000 decisions per day. Daily cost: $42,875 (floor) to $980,000 (ceiling). Annual cost: $15.6 million (floor) to $357.7 million (ceiling).

Health System scale: 1,000,000 decisions per day. Daily cost: $428,750 (floor) to $9.8 million (ceiling). Annual cost: $156.5 million (floor) to $3.58 billion (ceiling).

Sovereign Large scale: 10,000,000 decisions per day. Daily cost: $4.3 million (floor) to $98 million (ceiling). Annual cost: $1.56 billion (floor) to $35.8 billion (ceiling).

Applying the 1.36x variance multiplier: the effective Health System annual cost at the floor becomes $212.8 million. Effective Sovereign Large annual cost at the floor becomes $2.13 billion.

### 3.4 Scale point cost comparison: substrate side

Per full-stack decision, deterministic substrate validation costs **15.9 to 48.8 milliseconds of CPU**, measured across a simple model (Employment-Record) and a complex one (Healthcare-Record) at small, medium, and large instance sizes. Translated at a representative cloud rate ($0.048/vCPU-hour) and an amortized on-prem rate ($0.014/vCPU-hour):

| Model | Size | Full-stack CPU (ms) | $/decision (cloud) | $/decision (on-prem) | Verdict variance |
| :---- | :---- | ----: | ----: | ----: | :---- |
| Employment-Record | small | 15.9 | $2.1×10⁻⁷ | $6.2×10⁻⁸ | 0 (by construction) |
| Employment-Record | medium | 23.6 | $3.2×10⁻⁷ | $9.2×10⁻⁸ | 0 (by construction) |
| Employment-Record | large | 30.7 | $4.1×10⁻⁷ | $1.2×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | small | 34.8 | $4.6×10⁻⁷ | $1.4×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | medium | 42.2 | $5.6×10⁻⁷ | $1.6×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | large | 48.8 | $6.5×10⁻⁷ | $1.9×10⁻⁷ | 0 (by construction) |

Projected across the five scale points (Healthcare-Record, medium instance, full-stack), against the inference-side annual totals from Section 3.3:

| Scale point | Decisions/day | SDC annual (cloud) | SDC annual (on-prem) | Inference annual (floor–ceiling) |
| :---- | ----: | ----: | ----: | ----: |
| Pilot | 2,400 | $0.49 | $0.14 | $375,585 – $8.6M |
| Department | 10,000 | $2.05 | $0.60 | $1.6M – $35.8M |
| Hospital | 100,000 | $20.55 | $5.99 | $15.6M – $357.7M |
| Health System | 1,000,000 | $205.49 | $59.94 | $156.5M – $3.58B |
| Sovereign Large | 10,000,000 | $2,054.93 | $599.35 | $1.56B – $35.8B |

The per-decision gap is six to seven orders of magnitude. At Health System scale (1 million decisions per day), the substrate-side costs are on the order of $200 per year on commodity cloud, or $60 per year amortized on-premises, compared to the inference side's $156.5 million to $3.58 billion per year. The gap widens with scale exactly as Section 4.1 predicts: inference cost is linear per decision, while deterministic CPU cost is approximately constant per decision and amortizes against fixed infrastructure.

On verdict variance, the substrate side returned an identical verdict on every repeated evaluation of identical input, across all instances and sizes — zero variance by construction, a re-run multiplier of 1.0. The inference side's 1.36x average (3 to 5x worst case) re-run tax to reach a defensible repeatable verdict, therefore, falls on one side of this comparison only.

Two notes on scope. The cost bases above are parameters; the per-decision order-of-magnitude estimate is robust to them, since even a tenfold change in the vCPU rate leaves a five-to-six-order-of-magnitude gap. And the SHACL component of BIS reasons over the model's published constraint shapes, so it scales with model complexity rather than instance size, while the validation work in CSAS and ACPS scales with instance size; the figures reflect both.

## 4\. Discussion

### 4.1 The structural argument

The gap between inference-based and deterministic governance is not incremental. It is structural for three reasons.

First, inference cost is linear per decision. Each decision requires a fresh set of API calls. CPU cost for deterministic validation is approximately constant per decision at volume. Fixed infrastructure amortizes across all decisions. The gap widens with scale, not closes.

Second, inference-based evaluation carries irreducible verdict variance. Deterministic evaluation has zero variance by construction. This is an architectural property, not an implementation choice. No engineering effort can eliminate variance in a probabilistic system without converting it to a deterministic one.

Third, sovereign and air-gapped deployments face an additional multiplier on the inference side. Either sovereign LLM hosting costs (GPU infrastructure) or external API call costs (latency and data sovereignty issues). Deterministic validation runs locally with no external dependency. No GPU required. No API latency. No data leaving the sovereign boundary.

These three structural differences compound at scale. They are not addressable through pricing negotiations or engineering optimization. They follow from the fundamental difference between probabilistic inference and deterministic computation.

Fourth, the CPU benchmark data is independently reproducible from the open repository at github.com/Axius-SDC/substrate-economics. The inference-side cost estimates are derived from protocol-based token consumption estimates, validated against the probe structure. The deterministic side costs derive from independently verifiable benchmarks. The evidentiary asymmetry strengthens the structural argument: one side is checkable from open source; the other is an estimate from a published protocol.

### 4.2 Implications for procurement

Three implications follow for regulated enterprises and sovereign procurement evaluators.

First: governance validation cost should be included in the total cost of ownership calculations for AI deployment at scale. Most current evaluations exclude it. A model that costs $0.001 per inference call still costs $0.43 to $9.80 per governed decision. The governance overhead exceeds the inference cost by orders of magnitude at the full-stack level.

Second: vendor assurance of model governance reliability does not meet MDR and NMI defensibility requirements. Independently produced repeatable verdicts are required. The re-run multiplier is a compliance cost, not a quality-of-life issue. It must be budgeted explicitly.

Third: substrate-first governance architecture is not just architecturally and intellectually preferable. It is economically necessary at the health system and sovereign scales. The cost difference at 1 million decisions per day is not marginal. It is the difference between a viable operating cost and an impossible one.

### 4.3 Limitations

The inference-side token counts are protocol-based estimates, not values metered from the evaluation database. They are validated against probe structure but not measured directly per call. Independent reproduction of the open benchmark, and direct metering where feasible, would tighten the inference-side figures.

The decisions-per-day denominator is the most contestable input. Whether every clinical interaction constitutes a full governance decision is a deployment-specific question. Annual totals are presented as ranges with the denominator exposed for this reason, and should not be read as point predictions.

The cost bases are representative parameters, not universal rates. Volume discounts, reserved capacity, and negotiated agreements move them. The per-decision order-of-magnitude estimate is robust to such movement: even a tenfold change in the vCPU rate leaves a five- to six-order-of-magnitude gap.

The substrate benchmark uses a single reference deployment (CordovaOS, two models) on commodity hardware, on the offline FOSS-equivalent path. Broader stack profiles, larger model libraries, and fuller payload and policy-complexity curves remain to be characterized.

The variance characterization covers 35 models at two sampling temperatures. It is a snapshot of a model landscape that is continuously evolving, and the specific multipliers will shift as models are released and revised.

Finally, where deterministic validation and LLM evaluation do not perform identical work for a given class, the comparison is scoped to the governance decision both architectures are asked to render, and the difference is documented rather than claimed as strict equivalence.

## 5\. Conclusion

Runtime governance validation cost differs by orders of magnitude between deterministic substrate-based and inference-based approaches.

The variance finding is the hardest to dispute. Deterministic substrate validation meets the repeatable verdict requirement by construction. Inference-based evaluation imposes a structural tax on its approach. The tax is 1.36x on average and 3-5x in the worst case.

At the regional-health-system scale, the annual cost difference is material. At the sovereign scale, it is prohibitive. The compliance argument is structural. It does not depend on pricing negotiations or engineering improvements.

The economic case for substrate-first governance is independent of the architectural and intellectual cases. It survives scrutiny at the buyer-room level. Combined with the architectural and intellectual arguments, the three dimensions make a complete case.

## Data and Code Availability

The substrate-side benchmark — harness, fixtures, raw timing data, and the environment manifest (hardware, operating system, and pinned component versions) — is published in the open repository at github.com/Axius-SDC/substrate-economics and is independently reproducible. The reported substrate-side figures are being verified against an independent reproduction run before publication.

The inference-side data derives from the MTCP evaluation corpus and protocol (DOI: 10.17605/OSF.IO/DXGK5). Token consumption figures are protocol-based estimates as described in Section 2.3.

## References

Abby, A. (2026). Multi-Turn Constraint Persistence: Formal Framework. DOI: 10.17605/OSF.IO/DXGK5.

Abby, A. (2026). MTCP Paper 32: Remediation Effectiveness Score. DOI: 10.17605/OSF.IO/DXGK5.

Abby, A. and Cook, T.W. (2026). Constraint-State Evidence and Governed Execution. DOI: 10.17605/OSF.IO/DXGK5.

Cook, T.W. (2026). SDC Governance Architecture. Axius SDC, Inc.

Cook, T.W. (2026). Substrate Economics Benchmark: code, fixtures, and data. github.com/Axius-SDC/substrate-economics.

EU MDR 2017/745 Article 22: Obligation of the Responsible Person.

Swedish NMI (2026). Per-Decision Compliance Requirements for AI-Assisted Clinical Decision Support.

## Appendix A: Glossary of Abbreviations

**SDC (substrate) side**

- **SDC** — Semantic Data Charter: the open-standard data substrate; constraints, governance, and provenance bound to the data payload.  
- **SDCStudio** — the SDC modeling and publishing platform (referenced re: the rate-setting observation).  
- **sdcvalidator** — SDC library performing structural validation of a data instance against its model (Apache-2.0, pure Python).  
- **sdcgovernance** — SDC library performing runtime governance: XACML access decisions and a hash-chained Receipt corpus (Apache-2.0, pure Python).  
- **Receipt corpus** — sdcgovernance's hash-chained, tamper-evident record of each governance decision.  
- **CordovaOS** — the SDC reference deployment used for the benchmark: ten cross-domain government data models generated from one reference model.

**MTCP (inference) side**

- **MTCP** — Multi-Turn Constraint Persistence: the measurement program whose evaluation corpus supplies the inference-side data.  
- **BIS** — the per-decision class measuring constraint persistence across a full multi-turn interaction (single system).  
- **CSAS** — Cross-System Admissibility: the per-decision class measuring constraint persistence at a coordination boundary between two systems.  
- **ACPS** — the per-decision class measuring constraint persistence under adversarial pressure.  
- **COS** — Constraint Object Specification: a constitutional-layer framework (design-time, established once).  
- **LRP** — Legitimacy Resolution: a constitutional-layer framework (design-time).  
- **GRC** — Governance Reference Conditions: a constitutional-layer framework (design-time). Distinct from the common "Governance, Risk, and Compliance."  
- **DRA** — Deployment Readiness Attestation: a periodic assessment (scheduled, not per decision).  
- **TDS** — a periodic MTCP assessment (scheduled, not per decision).  
- **BEC** — Behavioural Evidence Chain: hash-chained evidence operations; negligible per-decision CPU.  
- **Admissibility Gate** — a threshold lookup at the decision boundary, not an inference call.

**Standards**

- **XACML** — eXtensible Access Control Markup Language (OASIS): policy language for PERMIT / DENY access decisions.  
- **SHACL** — Shapes Constraint Language (W3C): validates data against constraint shapes.  
- **OWL** — Web Ontology Language (W3C).

**Regulatory**

- **EU MDR** — European Union Medical Device Regulation (Regulation 2017/745); Article 22 concerns obligations of the responsible person.  
- **NMI** — the Swedish national regulatory requirements cited here for per-decision defensibility in AI-assisted clinical decision support (see References).  
  


  
**Technical/general**

- **CPU-bound** — cost is processor time. **Inference-bound** — cost is per-call model inference (tokens).  
- **LLM** — large language model.  
- **vCPU** — virtual CPU; the cloud pricing unit ($/vCPU-hour).  
- **TCO** — total cost of ownership.  
- **token** — the unit of LLM input/output that inference is billed on.  
- **T** — an LLM's sampling temperature (e.g., T=0.0 leans deterministic, T=0.8 is more random).  
- **DOI** — Digital Object Identifier (a persistent citation identifier).

