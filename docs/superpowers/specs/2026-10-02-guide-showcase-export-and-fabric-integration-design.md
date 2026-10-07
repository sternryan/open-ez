# Guide Showcase, inspection, export and render-tooling integration

Status: proposed, engineering-reviewed 2026-10-02 (`DONE_WITH_CONCERNS`).
Parent: `docs/superpowers/specs/2026-09-29-roadmap-same-airplane-new-process-design.md`.
Near-term dependency:
`docs/superpowers/specs/2026-10-01-block2-m25-spar-firewall-controls-trim-design.md`.
Management counterpart: the render-tooling repo, "Open-EZ workload profiles and attended model
evaluation" (2026-10-02). The management repository owns implementation and release of the
compute interface described here.

## 1. Intent

Finish M2.5, then turn the existing build-rehearsal lab into a deterministic, provenance-aware
product demonstration and inspection tool. The same semantic scene state should drive chapter
tours, a cross-chapter Showcase, assembly inspection, shareable links, recording and visualization
exports. Manufacturing exports follow only after the corresponding CadQuery solids are physically
eligible.

Remote CPU, browser and GPU work is optional acceleration. Open-EZ describes workload
requirements and consumes a pinned, released interface. It does not own fleet placement,
credentials, remote paths, locking, model routing or paid-provider policy.

## 2. Review findings that change the plan

### 2.1 Execution identity is not content identity

`guide/render_cutaway.sh` currently derives a remote directory from a content key and removes it
before dispatch. Two executions with the same content can therefore collide. `scripts/remote_test.sh`
likewise relies on a shared mutable checkout and environment.

Three identities must remain distinct:

1. the Open-EZ source/configuration revision;
2. the digest of reusable inputs or completed artifacts; and
3. the unique execution attempt that produced an artifact.

The management interface must allocate unique attempt workspaces. A completed content-addressed
cache may be shared only after atomic publication. Open-EZ wrappers must stop managing shared
remote directories once the released interface exists.

### 2.2 Display geometry is not manufacturing geometry

The lab converts inches to glTF metres, clones and poses installed assemblies, and uses visual
effects that do not necessarily modify the solid. The M2.4 elevator cove is shader-only, for
example. A downloaded raw GLB therefore does not automatically reproduce the visible assembly and
is not fabrication-ready.

The first export is a visualization package: canonical GLB plus a manifest declaring revision,
units, axes, identities, transforms, represented state, fidelity and visual-only effects. STEP and
STL come later from eligible CadQuery solids.

### 2.3 Recording must fail closed

`guide/lab/tools/record.mjs` waits for ffmpeg to close but does not check its exit status before
reporting success. Recording must treat browser, page and encoder errors as failures, bound runtime,
clean up children, validate the resulting media, and atomically publish the video with a completion
manifest.

### 2.4 Declarative films cannot silently skip actions

The existing director tolerates absent selector and drag targets. Film data must instead reference
semantic action, operation and shot IDs. A compiler validates those references and produces the
existing `Step[]`; a missing required target fails before playback.

### 2.5 M2.5 has an insertion-direction contradiction

The M2.5 design says the spar enters from the rear in section 3 and from the side in section 4.
Resolve this against the cited evidence before authoring the animation. Do not choose the more
convenient motion and treat it as source truth.

### 2.6 Shards must not hide isolation defects

The M2.4 report records possible order-dependent CadQuery mock leakage in a single process. Reproduce
or dismiss it before claiming the full suite passes. Remote shards must publish a collection
manifest proving that the intended suite ran exactly once; sharding is not a substitute for fixing
test isolation.

## 3. Ownership boundary

| Concern | Open-EZ owns | Management interface owns |
|---|---|---|
| Geometry and provenance | configuration, solids, fidelity and source meaning | no reinterpretation |
| Rehearsal content | graph, semantic actions, films and expected artifacts | execution of declared profiles |
| Public transfer | allowlisted public input bundle and acceptable public output | enforcement, staging and sanitized evidence |
| Job interface | pinned client/schema consumption and application acceptance | schema, client and profile releases |
| Execution | requirements and limits | workspaces, leases, retries, cancellation and cleanup |
| Models | bounded task and acceptance rubric | routing, entitlements, budgets and audit |
| Infrastructure identity | absent from tracked files | private configuration |
| Promotion | application gates and authorized publish workflow | runner/profile promotion workflow |

Open-EZ must contain no credentials, fleet names, addresses, private paths, scans, OCR or private
source-corpus material. Application-specific geometry and render logic remains attributable to this
repository; the management runner stays generic.

## 4. Consumed workload contract

Open-EZ expects a closed, versioned task envelope equivalent to:

```json
{
  "schema_version": "fabric-task-v1",
  "job_id": "UUID",
  "attempt_id": "UUID",
  "consumer": "open-ez",
  "source": {
    "revision": "COMMIT",
    "bundle_sha256": "SHA256"
  },
  "profile": {
    "id": "browser-record",
    "version": "1",
    "implementation_sha256": "SHA256"
  },
  "inputs": [
    {
      "name": "site",
      "artifact_ref": "OPAQUE_APPROVED_REFERENCE",
      "sha256": "SHA256",
      "bytes": 1234
    }
  ],
  "parameters": {
    "film_id": "showcase-v1",
    "film_sha256": "SHA256",
    "fps": 60,
    "width": 1920,
    "height": 1080,
    "quality": "high"
  },
  "requirements": {
    "capabilities": ["browser.chromium", "render.gpu"],
    "privacy": "public-only",
    "network": "none",
    "paid_access": false
  },
  "limits": {
    "wall_ms": 1800000,
    "artifact_bytes": 1073741824,
    "usd_micros": 0,
    "model_tokens": 0,
    "attempts": 1
  },
  "outputs": ["video", "execution-manifest"]
}
```

This is a consumer requirement, not an existing endpoint. Profile parameters also use closed
schemas. Unknown fields, path traversal, unsupported versions, non-finite numbers, changed input
digests and unbounded collections are rejected.

The result must include job/attempt/input identity, profile/runtime versions, output hashes and
sizes, timing, exit status, validation results and structured failure codes. Private execution
metadata is separate from the sanitized evidence that Open-EZ may retain.

## 5. Executable plan

### OE0 — Freeze M2.5 invariants

Dependencies: none.

- Inventory all M2.5 operations, components, evidence, expected visible changes and remaining
  `no-geometry` entries.
- Resolve the insertion direction and record chapter 4–9 behavior affected by new dependencies.
- Define stable component IDs, physical/display representation and coordinate transforms.
- Record the actual suite state, intentional strict xfails, public-build checks and representative
  frames; investigate the reported mock leak.
- Identify source gaps that block fabrication exports.

Done when every missing solid and representational item appears in an operation/component matrix,
and no provenance flag changes without a source page.

### OE1 — Complete M2.5 solids

Dependencies: OE0.

- Add the spar model around `core/spar_kin.py`: box, cap plies, hard points and LWA parts.
- Add firewall-face and control/trim solids around existing configuration and
  `core/controls_kin.py`.
- Keep unavailable outlines, placements, stops and hardware visibly representational.
- Extend export and layup metadata; replace deliberate `no-geometry` assertions with per-component
  geometry and fidelity expectations.
- Keep the sourced prototype spar mass distinct from computed mass and ledger lower bounds.

Done when intended volumetric solids are valid with positive volume; stations, symmetry, cap
schedules, travel and transforms have independent numerical assertions; Roncz values never inherit
GU values; and no unavailable attach station or stop is invented.

### OE2 — Complete the M2.5 lab and release evidence

Dependencies: OE1; the released management interface only if remote execution is used.

- Add spar construction, cap laydown, fitting/bonding, firewall hardware, stick/elevator motion and
  trim.
- Add operation shots, section cuts, labels, chapter 14–17 tours and the spar-fitting film.
- Preserve conflicts and representational parts under selection, isolation and cutaways.
- Fix recorder failure handling before recording release evidence.
- Run independent visual review, application gates, reports and the authorized publish workflow.

Done when every operation changes the intended state or explains why it adds no solid; phone-width,
desktop and WebKit checks pass; any iPad performance claim has actual iPad evidence; public and
private-source gates pass in their intended environments; known physics failures remain strict; and
recorded artifacts identify the source revision and hashes.

### OE3 — Semantic state and declarative films

Dependencies: OE2 baseline; schema design may start after OE0.

- Put a small semantic action boundary around subject, operation, cut, camera, pose and selection.
- Validate declarative film documents and compile them to the existing director.
- Add readiness barriers for geometry, fonts and assets.
- Implement reset and fixed-tick replay for deterministic seeking.
- Handle stop, interruption, replay, missing references and reduced motion explicitly.

Done when the same revision, film, tick and settings produce the same serialized scene state;
unknown IDs and conflicting actions fail; replay does not overwrite saved preferences; and existing
chapter films remain covered.

### OE4 — Showcase and provenance-aware metric beats

Dependencies: OE3.

- Compose a cross-chapter Showcase from existing subjects and selected M2.5 beats.
- Use the reference CAD demonstration for interaction and pacing inspiration only, never as
  dimensional evidence.
- Resolve metric cards through a registry backed by configuration, reports and ledgers.
- Present value, unit, scope, source status and validation status together.
- Explain omitted chapters and unavailable results.

Done when film documents contain no duplicated engineering values; stale or absent reports fail
resolution; conflicts show both values; prototype mass is never presented as measured model mass;
and unavailable CG stays unavailable.

### OE5 — Assembly inspector and shareable state

Dependencies: OE1 identity model and OE3 actions.

- Build an assembly hierarchy from semantic IDs.
- Synchronize tree and viewport selection; add isolate, reset and explicit explode transforms from
  immutable rest poses.
- Show provenance, fidelity and unresolved issues in the inspector.
- Encode a bounded, versioned URL state for public IDs, subject, operation, cut, selection, camera
  and presentation preferences.
- Bind links to the model revision/digest so old links cannot silently address new geometry.

Done when selection stays synchronized; repeated explode/reset has no drift; isolation preserves
fidelity markings; Escape and browser history work; and malformed/stale links recover visibly.

### OE6 — Visualization export

Dependencies: OE5 and validated transforms.

- Export a canonical visualization GLB and manifest.
- Declare units, axes, revision, included content, transforms, provenance, fidelity and known
  visual-only effects.
- Default to an intelligible assembly pose and distinguish deliberate exploded-state exports.
- Exclude workshop geometry unless requested explicitly.
- Re-import the package with an independent consumer.

Done when round-trip checks catch scale/axis errors; every node maps to a manifest identity; hashes
validate; shader-only omissions are disclosed; the package makes no fabrication-ready claim; and
the public leakcheck covers GLB JSON chunks and package metadata.

### OE7 — STEP/STL and Block 4 preparation

Dependencies: OE6, corrected physical solids and the roadmap gates appropriate to the article.

- Export STEP/STL from CadQuery with units, tolerances, sources and eligibility metadata.
- Begin with non-structural samples and permitted scale prototypes.
- Separate display tessellation from manufacturing tolerances.
- Add sectioning, registration and fit checks against a verified printer profile.
- Evaluate pinned DFM/DfAM and slicer tools through explicit input/output contracts.

Done when manifold, dimensional and planted-defect gates work; registration survives assembly
checks; and representational or conflicted geometry is excluded from fabrication-critical release.
Software checks do not replace material testing, hardware comparison or independent engineering
review.

## 6. Verification matrix

1. M2.5 solids, numerical invariants and fidelity.
2. Timeline schema, semantic actions, reset, replay and interruption.
3. Metric provenance, unavailable values and revision binding.
4. Tree, isolation, explode and URL recovery.
5. GLB/STEP/STL identity, units, completeness and public hygiene.
6. Workload collision, cancellation and exact test-collection evidence.
7. Recorder/encoder failure and incomplete-artifact rejection.
8. Public-only transfer and sanitized execution evidence.

Every new gate counts only after a planted failure proves it can fail.

## 7. Delegation

Bounded agents may own schema fixtures, URL parsing, pure transforms, manifest validators, recorder
failure tests, deterministic numerical helpers and generated schema documentation. Strong review is
required for source interpretation, fidelity changes, geometry, coordinate/export semantics,
fabrication eligibility, visual sign-off and release claims. Builders do not grade their own output.

## 8. Ordering

OE0 and the management contract/isolation work start together. OE1 may run in parallel with the
management implementation. OE3 begins after the semantic identity contract stabilizes; OE4 and OE5
follow it. OE6 precedes OE7. Remote acceleration is never a prerequisite for local correctness.

## 9. Not in scope

- Replacing the director, Three.js or CadQuery.
- Adding fleet management, credentials or provider routing to this repository.
- Building a distributed queue, general agent platform or multi-user CAD system.
- Resolving source conflicts automatically or widening physics bounds.
- Completing the canopy, wings, winglets or remaining chapters inside M2.5.
- Certified manufacturing data, automatic printer starts, structural equivalence or flightworthiness
  claims.
- Paid model calls as part of this design record.

## 10. Decision log

- Reuse the director and semantic lab state rather than add a demo-only animation stack.
- Keep execution attempt identity separate from source and artifact identity.
- Consume a released generic compute interface; keep infrastructure private and management-owned.
- Export a disclosed visualization package before manufacturing formats.
- Make source status and validation status separate and visible.
- Permit paid open-weight evaluation only through an attended, budgeted management profile.
