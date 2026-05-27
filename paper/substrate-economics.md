# Substrate Economics

## The Token-Cost Asymmetry Between Deterministic and Inference-Based Governance

**Timothy W. Cook**, Axius SDC, Inc.
**Ahmad Abby**, MTCP Research Programme

Contact: admin@mtcp.live
DOI: 10.17605/OSF.IO/DXGK5
May 2026

---

## Abstract

Runtime governance validation costs differ by orders of magnitude depending on validation type. Deterministic CPU-bound validation and inference-based LLM-bound validation occupy different cost regimes entirely.

This note quantifies the per-decision cost gap. It uses empirical token consumption data from 183,924 MTCP evaluations and an SDC CPU benchmark. The gap is structural not incremental. It widens at scale.

A second structural difference is verdict variance. Deterministic substrate validation produces zero verdict variance by construction. It meets MDR and NMI repeatable verdict requirements automatically. Inference-based evaluation carries an average 1.36x re-run multiplier across 35 models. Worst-case multipliers reach 3 to 5x on high-variance models.

The combined cost and variance argument constitutes an economic case for substrate-first governance. This case is independent of architectural and intellectual arguments.

## 1. Why This Argument and Why Now

The substrate-first thesis has been argued on two dimensions. Architectural: deterministic validation provides provable correctness. Intellectual: schema-based reasoning captures constraint semantics formally. This note opens a third dimension. Economics.

The recognition is not new. It surfaced during SDCStudio rate-setting. Most validation cost was CPU time not inference. What is new is the scale that makes it matter.

Region Stockholm runs approximately 8 million doctor visits annually. It runs approximately 490,000 emergency visits annually. Seven hospitals operate with executive-approved AI-assisted decision support. EU MDR and Swedish NMI impose per-decision compliance overhead.

At that volume the per-decision cost difference compounds. It compounds into materially different total cost of ownership. The argument has moved from abstract to buyer-room.

This note presents the inference-side cost data from MTCP empirical measurements alongside the SDC CPU benchmark data. The comparison is the argument.

## 2. Scope and Precision: Runtime Versus Design-Time

The cost argument applies to the runtime governance layer only. Not all governance operations are per-decision. The distinction matters.

Three MTCP evaluation types constitute per-decision runtime inference. BIS measures constraint persistence across a full multi-turn interaction. CSAS measures constraint persistence at coordination boundaries between two systems. ACPS measures constraint persistence under adversarial pressure.

All other MTCP layers are design-time, periodic, or negligible-cost operations. Constitutional layer frameworks (COS, LRP, GRC) are design-time definitions established once. They are not per-decision. DRA and TDS are periodic assessments. They run at scheduled intervals not per decision. BEC hash-chain operations are negligible CPU cost. The Admissibility Gate is a threshold lookup not an inference call.

On the SDC side the runtime layer is deterministic and CPU-bound. The sdcvalidator validates payload structure. The sdcgovernance XACML engine evaluates access policies. SHACL and OWL reasoning validates schema constraints. Receipt corpus hash-chain operations provide tamper evidence. All are CPU-bound at runtime.

The SDC Agents suite uses LLMs at design-time. That is a different layer with different economics. Runtime governance validation is the comparison subject throughout this note.

## 3. Per-Decision Cost Analysis: Inference Side

Token consumption per evaluation type is estimated from the standard MTCP protocol structure. Actual token counts are not stored in the evaluation database. Estimates are validated against probe structure.

BIS evaluation: 350 input tokens and 500 output tokens per evaluation. Total 850 tokens. The three-turn protocol delivers the constraint, applies correction, and assesses final compliance.

CSAS evaluation: 700 input tokens and 1,000 output tokens. Total 1,700 tokens. Two models each run the full three-turn protocol.

ACPS evaluation: 1,200 input tokens and 1,000 output tokens. Total 2,200 tokens. Four adversarial attack types each require structured prompts longer than standard probes.

Full-stack per-decision evaluation requires all three types. Total tokens: 4,750 per decision.

Cost per BIS evaluation ranges from $0.082 (Nova Micro tier) to $1.88 (Nova Pro tier). Cost per full-stack decision ranges from $0.43 (floor) to $9.80 (ceiling). The floor uses the cheapest provider: AWS Bedrock Nova Micro. Pricing is $0.035 per 1,000 input tokens and $0.14 per 1,000 output tokens. The ceiling uses the most expensive tier (Nova Pro at $0.80 per 1,000 input and $3.20 per 1,000 output).

Cost per million BIS evaluations: $82,250 (floor) to $1,880,000 (ceiling). Cost per million full-stack decisions: $428,750 (floor) to $9,800,000 (ceiling).

These are order-of-magnitude estimates. Volume discounts, reserved capacity, and provider-specific agreements reduce actual costs. The per-decision order of magnitude is the primary finding. Annual totals at scale follow as illustrations.

## 4. Verdict Variance: The Regulatory Cost Multiplier

This section presents the central argument.

Deterministic substrate validation produces zero verdict variance by construction. The same payload evaluated twice against the same schema and policy produces identical results. Every time. Without exception. This meets EU MDR Article 22 and Swedish NMI per-decision defensibility requirements automatically. No re-run cost multiplier applies.

Inference-based evaluation carries measurable verdict variance. The same model evaluated on the same constraint at the same temperature can produce different outcomes across runs. This is intrinsic to probabilistic inference not an implementation failure.

The MTCP corpus quantifies this variance across 35 models. Twenty-two models produce stable verdicts without re-runs. These are deterministic-equivalent in practice at T=0.0. Their variance between T=0.0 and T=0.8 is below 2 percent.

Eleven models show moderate variance between 2 and 10 percent. These require 1.5 to 2.0 re-runs for a defensible repeatable verdict. The affected model families include Claude, Qwen, Cohere, GPT-mini, Granite, Nova Pro, Phi, Gemma, Grok, and Llama-8b.

Two models show high variance above 10 percent. These require 3 to 5 re-runs for defensible verdicts. One model shows 34.9 percent delta between T=0.0 and T=0.8. It requires a 5.0x cost multiplier. Another shows 17.3 percent delta requiring a 3.0x multiplier.

The average re-run multiplier across all 35 models is 1.36x.

The inference side pays a tax to reach a defensibility standard the deterministic side meets by construction. Under frameworks requiring defensible repeatable verdicts this is not a cost optimisation problem. It is a regulatory architecture problem.

The 1.36x average multiplier and 3 to 5x worst case are structural features of inference-based evaluation. They are not implementation failures. They follow from the probabilistic nature of LLM inference. No amount of engineering eliminates verdict variance from a probabilistic system.

## 5. Scale Point Cost Comparison

Five scale points illustrate cost at increasing deployment volume. All figures use the full-stack evaluation (BIS plus CSAS plus ACPS) at floor and ceiling provider tiers.

Pilot scale: 2,400 decisions per day. Daily cost: $1,029 (floor) to $23,520 (ceiling). Annual cost: $375,585 (floor) to $8.6 million (ceiling).

Department scale: 10,000 decisions per day. Daily cost: $4,288 (floor) to $98,000 (ceiling). Annual cost: $1.6 million (floor) to $35.8 million (ceiling).

Hospital scale: 100,000 decisions per day. Daily cost: $42,875 (floor) to $980,000 (ceiling). Annual cost: $15.6 million (floor) to $357.7 million (ceiling).

Health System scale: 1,000,000 decisions per day. Daily cost: $428,750 (floor) to $9.8 million (ceiling). Annual cost: $156.5 million (floor) to $3.58 billion (ceiling).

Sovereign Large scale: 10,000,000 decisions per day. Daily cost: $4.3 million (floor) to $98 million (ceiling). Annual cost: $1.56 billion (floor) to $35.8 billion (ceiling).

Applying the 1.36x variance multiplier: effective Health System annual cost at floor becomes $212.8 million. Effective Sovereign Large annual cost at floor becomes $2.13 billion.

### 5.1 Scale Point Cost Comparison: Substrate Side

The SDC runtime-governance operations were benchmarked at the same five scale points, with the same per-decision composition (BIS + CSAS + ACPS), on valid governed instances of the CordovaOS government data models. BIS is composed of structural validation plus SHACL constraint reasoning plus a hash-chained receipt; CSAS adds an XACML governance advisory across a system boundary; ACPS adds the governance advisory under adversarial framing. Process CPU time was measured at N=1000 per class, fully offline — no triplestore, no GPU, no network. The benchmark, fixtures, and raw data are reproducible from the open repository (see References).

Per full-stack decision, deterministic substrate validation costs **15.9 to 48.8 milliseconds of CPU**, measured across a simple model (Employment-Record) and a complex one (Healthcare-Record) at small, medium, and large instance sizes. Translated at a representative cloud rate ($0.048/vCPU-hour) and an amortized on-prem rate ($0.014/vCPU-hour):

| Model | Size | Full-stack CPU (ms) | $/decision (cloud) | $/decision (on-prem) | Verdict variance |
|---|---|--:|--:|--:|:--|
| Employment-Record | small | 15.9 | $2.1×10⁻⁷ | $6.2×10⁻⁸ | 0 (by construction) |
| Employment-Record | medium | 23.6 | $3.2×10⁻⁷ | $9.2×10⁻⁸ | 0 (by construction) |
| Employment-Record | large | 30.7 | $4.1×10⁻⁷ | $1.2×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | small | 34.8 | $4.6×10⁻⁷ | $1.4×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | medium | 42.2 | $5.6×10⁻⁷ | $1.6×10⁻⁷ | 0 (by construction) |
| Healthcare-Record | large | 48.8 | $6.5×10⁻⁷ | $1.9×10⁻⁷ | 0 (by construction) |

Projected across the five scale points (Healthcare-Record, medium instance, full-stack), against the inference-side annual totals from section 5:

| Scale point | Decisions/day | SDC annual (cloud) | SDC annual (on-prem) | Inference annual (floor–ceiling) |
|---|--:|--:|--:|--:|
| Pilot | 2,400 | $0.49 | $0.14 | $375,585 – $8.6M |
| Department | 10,000 | $2.05 | $0.60 | $1.6M – $35.8M |
| Hospital | 100,000 | $20.55 | $5.99 | $15.6M – $357.7M |
| Health System | 1,000,000 | $205.49 | $59.94 | $156.5M – $3.58B |
| Sovereign Large | 10,000,000 | $2,054.93 | $599.35 | $1.56B – $35.8B |

The per-decision gap is six to seven orders of magnitude. At Health System scale (1 million decisions per day) the substrate side costs on the order of two hundred dollars per year on commodity cloud, or sixty dollars per year amortized on-premises, against the inference side's $156.5 million to $3.58 billion per year. The gap widens with scale exactly as section 6 predicts: inference cost is linear per decision, while deterministic CPU cost is approximately constant per decision and amortizes against fixed infrastructure.

On verdict variance, the substrate side returned an identical verdict on every repeated evaluation of identical input, across all instances and sizes — zero variance by construction, a re-run multiplier of 1.0. The inference side's 1.36x average (3 to 5x worst case) re-run tax to reach a defensible repeatable verdict therefore falls on one side of this comparison only.

Two notes on scope. The cost bases above are parameters; the per-decision order of magnitude is robust to them, since even a tenfold change in the vCPU rate leaves a five-to-six order-of-magnitude gap. And the SHACL component of BIS reasons over the model's published constraint shapes, so it scales with model complexity rather than instance size, while the validation work in CSAS and ACPS scales with instance size; the figures reflect both.

## 6. The Structural Argument

The gap between inference-based and deterministic governance is not incremental. It is structural for three reasons.

First, inference cost is linear per decision. Each decision requires a fresh set of API calls. CPU cost for deterministic validation is approximately constant per decision at volume. Fixed infrastructure amortises across all decisions. The gap widens with scale not closes.

Second, inference-based evaluation carries irreducible verdict variance. Deterministic evaluation has zero variance by construction. This is an architectural property not an implementation choice. No engineering effort eliminates variance from a probabilistic system without converting it to a deterministic one.

Third, sovereign and air-gapped deployments face an additional multiplier on the inference side. Either sovereign LLM hosting costs (GPU infrastructure) or external API call costs (latency and data sovereignty issues). Deterministic validation runs locally with no external dependency. No GPU required. No API latency. No data leaving the sovereign boundary.

These three structural differences compound at scale. They are not addressable through pricing negotiations or engineering optimisation. They follow from the fundamental difference between probabilistic inference and deterministic computation.

## 7. Implications for Procurement

Three implications follow for regulated enterprise and sovereign procurement evaluators.

First: governance validation cost should be included in total cost of ownership calculations for AI deployment at scale. Most current evaluations exclude it. A model that costs $0.001 per inference call still costs $0.43 to $9.80 per governed decision. The governance overhead exceeds the inference cost by orders of magnitude at the full-stack level.

Second: vendor assurance of model governance reliability does not meet MDR and NMI defensibility requirements. Independently produced repeatable verdicts are required. The re-run multiplier is a compliance cost not a quality-of-life issue. It must be budgeted explicitly.

Third: substrate-first governance architecture is not just architecturally and intellectually preferable. It is economically necessary at health system and sovereign scale. The cost difference at 1 million decisions per day is not marginal. It is the difference between a viable operating cost and an impossible one.

## 8. Conclusion

Runtime governance validation cost differs by orders of magnitude between deterministic substrate-based and inference-based approaches.

The variance finding is the hardest to dispute. Deterministic substrate validation meets the repeatable verdict requirement by construction. Inference-based evaluation pays a structural tax to approach it. The tax is 1.36x on average and 3 to 5x in the worst case.

At Region Stockholm scale the annual cost difference is material. At sovereign scale it is prohibitive. The compliance argument is structural. It does not depend on pricing negotiations or engineering improvements.

The economic case for substrate-first governance is independent of the architectural and intellectual cases. It survives scrutiny at the buyer-room level. Combined with the architectural and intellectual arguments the three dimensions make a complete case.

## References

Abby, A. (2026). Multi-Turn Constraint Persistence: Formal Framework. DOI: 10.17605/OSF.IO/DXGK5.

Abby, A. (2026). MTCP Paper 32: Remediation Effectiveness Score. DOI: 10.17605/OSF.IO/DXGK5.

Abby, A. and Cook, T.W. (2026). Constraint-State Evidence and Governed Execution. DOI: 10.17605/OSF.IO/DXGK5.

Cook, T.W. (2026). SDC Governance Architecture. Axius SDC, Inc.

Cook, T.W. (2026). Substrate Economics Benchmark: code, fixtures, and data. github.com/Axius-SDC/substrate-economics.

EU MDR 2017/745 Article 22: Obligation of the Responsible Person.

Swedish NMI (2026). Per-Decision Compliance Requirements for AI-Assisted Clinical Decision Support.
