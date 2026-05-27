# PRD — Benchmark Dataset & Fixtures

**For discussion.** Decides what data models, governance components, payloads, and policies the CPU benchmark runs against, and how much infrastructure to stand up. Pairs with `METHODOLOGY.md`.

**Status:** proposal, 2026-05-27. Recommendation is marked; open questions at the end.

---

## 1. What the fixtures must enable

The benchmark's comparable unit is **process CPU time per runtime governance decision**, measured so it sits directly beside the MTCP inference side's **tokens per decision**. The fixtures therefore must:

- Exercise the real runtime components — `sdcvalidator`, `sdcgovernance` (XACML + Receipt corpus), SHACL/OWL reasoning — against realistic SDC4 models, not toy schemas.
- Cover every decision class in `METHODOLOGY.md` §3 with a concrete scenario.
- Be **isolatable**: the measurement must capture the governance computation, not app-server, DB-I/O, or network overhead, or the per-decision number is not comparable to a clean inference number.
- Be **reproducible and publishable**: committed to the repo so the result is independently checkable.

## 2. Source material (available today)

**CordovaOS — ten cross-domain government registries** (`~/GitHub/CordovaOS/models/`): Business-Registry, Civil-Registry, Education-Record, Employment-Record, Healthcare-Record, Law-Enforcement-Record, Maritime-Port-Authority, Property-Registry, Tax-and-Revenue-Record, Vital-Statistics-Record. All generated from one SDCRM, so they interoperate by construction. This is ideal: regulated + sovereign + cross-boundary, the paper's exact audience, and the decision classes have natural scenarios across these domains.

**ProvGov governance families** — the @ProvGov component families (sourced from CordovaOS templates; see `CordovaOS/docs/design/Governance_Rebuild_Plan.md`). Composing these into a data model is what makes it exercise the full runtime governance stack (XACML authority, provenance, receipts) rather than structural validation alone. Authoritative current definitions are in the SDCStudio Cloud SQL backup `sdcstudio_cloudsql_20260527_171128.sql.gz` (77 MB).

**Payload generation** — `CordovaOS/datagen/` for representative instances at varying sizes.

## 3. The decision (the fork to settle)

**Option A — Copy the models, compose ProvGov, mint new CUIDs for the composed models only (RECOMMENDED).**
Take a copy of the CordovaOS models and compose the @ProvGov families into them. **Mint new CUIDs only for the composed data-model schemas** — each composed model is a genuinely new artifact, because adding the ProvGov components changes the schema from the original. **Reuse every constituent component CUID unchanged** (both the CordovaOS components and the ProvGov components): they already have valid CUIDs, and reuse-by-reference preserves their identity as long as we do not edit them in situ. Exercise `sdcvalidator` + `sdcgovernance` + the runtime reasoner (Jena/Fuseki) directly via the harness against generated payloads and policy sets. No full Django app, no full DB restore — extract only the ProvGov family definitions from the backup.
- **Pro:** isolates per-decision CPU (the comparable number); reproducible; publishable; fits the 2-day window; reusing the real component CUIDs keeps the fixtures faithful (real components, real identities), while the newly minted model CUIDs do not collide with the live published namespace.
- **Con:** not a full in-situ system; does not capture real-deployment DB/app overhead (which is a feature here, not a bug, for the primary measurement).

**Option B — Stand up complete CordovaOS + restore ProvGov from the backup.**
Restore the 77 MB cloudsql dump, bring up the full Django project + ten apps + triplestore + DB, benchmark against the running system.
- **Pro:** maximum end-to-end realism; captures cross-app interoperation and real I/O.
- **Con:** app-server + DB-I/O + network overhead contaminate the clean CPU-per-decision figure and make it harder to defend and less comparable to a per-decision inference number; slower to stand up and control; more variables to hold constant; does not fit the 2-day window.

**Recommendation: Option A as the primary fixture and measurement. Option B as an optional v2 in-situ cross-check** (real-deployment throughput on the FOSS profile), reported separately if time allows, never as the primary comparison number. Versioned DOIs make adding the v2 cross-check later clean.

## 4. Fixture specification (Option A)

- **Models:** the ten CordovaOS registries, copied, with @ProvGov families composed in. New CUIDs are minted for the composed model schemas only (they differ from the originals because of the ProvGov composition); all constituent component CUIDs — CordovaOS and ProvGov alike — are reused unchanged (do not edit components in situ). Tag the fixture set with a version.
- **Payloads:** generated via `datagen` at three representative sizes (small / medium / large) per model, plus a few cross-domain instances (a subject appearing in Civil + Healthcare + Tax) for the handoff and jurisdiction classes.
- **Policy sets:** representative XACML policy sets at a small and a larger complexity, so cost-vs-policy-complexity is a measured curve, not a point.
- **Provenance chains:** receipts at several chain depths, so provenance-verification cost as a function of depth is captured.

**Decision-class → fixture scenario:**
| Decision class | Concrete scenario in this dataset |
|---|---|
| Schema validation | validate a Healthcare-Record instance against its model |
| Authority verification | XACML: can principal X read a restricted Tax-and-Revenue field |
| Constraint persistence | a derived Vital-Statistics value still holds its declared constraint |
| Provenance verification | trace a Civil-Registry record's lineage through the Receipt corpus |
| Cross-system handoff admissibility | a record crossing Healthcare → Tax → Law-Enforcement |
| Jurisdiction resolution | overlapping constraint sets when Maritime-Port-Authority and Business-Registry both govern an entity |

## 5. Harness & infrastructure (Option A)

Needed: `sdcvalidator`, `sdcgovernance`, a runtime reasoner (Apache Jena / Fuseki for the FOSS profile), and receipt storage. **Not** needed for the primary measurement: the full Django app layer, a full cloudsql restore. Pin every version in the manifest (`METHODOLOGY.md` §7).

## 6. Reproducibility & IP

- Commit the fixture set (models + composed ProvGov + payloads + policy sets) and the harness so the result is checkable. Fixtures and generated artifacts are Apache-2.0 (CordovaOS is already public). 
- **Confirm before publishing:** only the generated model/component definitions, payloads, and policies go in. None of the SDCStudio publisher/generator internals (proprietary) leak into the fixtures.

## 7. Open questions (for the discussion)

1. Confirm Option A vs B (recommendation: A primary, B optional v2).
2. ProvGov: extract family definitions from the backup, or reconstruct from CordovaOS templates / live SDCStudio? Which is the cleaner authoritative source?
3. Do we publish synthetic payloads only, or is any CordovaOS sample data already synthetic and safe to ship? (No real PII anywhere, obviously.)
4. Which decision classes are in scope for the **May 29 minimum publishable set** vs deferred to v2? (Proposal: schema validation, authority verification, provenance verification, and cross-system handoff for v1; constraint-persistence and jurisdiction-resolution can follow if time is short.)
5. Confirm the SDC-side decision classes map to the MTCP BIS / CSAS / ACPS labels (coordinate with Ahmad).
