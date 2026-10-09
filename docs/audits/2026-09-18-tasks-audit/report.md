# Audit of `tasks_audit`

Date: 18 September 2026. Scope: all eight task JSON files, their matching `ground_truth_fe` files, static and dynamic grading, and command hygiene. This is an audit, not a change to the benchmark. Task definitions, reference solutions, and grading code were left unchanged.

**The current tasks should not be treated as a reliable correctness benchmark without repairs.** Six of eight reference submissions pass locally, but one passing reference has the wrong physical volume, two references fail their numerical checks, valid equivalent submissions fail static checks, and some explicit geometric requirements are not enforced.

Confirmed findings below come from executable probes or direct inspection. Specification concerns are identified separately; they are not claims that every reference mesh violates those conditions.

## Reference results

Runs used the repository's actual `grade_submission` function and local Surface Evolver 2.70 (64-bit). Values are after the task's hidden script. All eight reference files pass static checks and complete the baseline Evolver run successfully.

| Task | Overall grade | Area | Energy | Main concern |
|---|---|---:|---:|---|
| `bridge_three_plates` | Pass | 3.893126852435 | 2.472398310772 | Literal algebra required despite allowing equivalents; initialization not fully specified |
| `bridge_two_rods` | Pass | 5.439578887871 | 4.744563962995 | Undefined convergence criterion and runtime budget; geometry not inspected |
| `cross_slot` | **Fail** | 1.280327459528 | **0.386448402871** | Expected energy is 0.511448402871 ± 0.05 |
| `cube` | Pass | 6 | — | Wrong location and an extra body also pass |
| `fiber_bridge_crossed` | Pass | 4.227259789086 | 3.269536054592 | Omitted horizontal-cylinder volume correction is not explained in the prompt |
| `pyramid_mound` | **Fail** | 3.975046736676 | **4.165328195716** | Expected energy is 4.079111342822 ± 0.05 |
| `square_well` | Pass | 1.138209036564 | 3.203926481513 | Bottom datum and unbounded-wall assumption need stating |
| `w_groove` | Pass | 5.331747030883 | 3.678007620352 | **Physical volume is approximately 1.86724, not 1** |

Full measurements, input hashes, and mutation results are in [evidence.json](/Users/yannhenon/code/surface-evolver-llm-eval/docs/audits/2026-09-18-tasks-audit/evidence.json). The [probe script](/Users/yannhenon/code/surface-evolver-llm-eval/docs/audits/2026-09-18-tasks-audit/probe.py) reproduces them without modifying benchmark inputs.

## Prioritized findings

### 1. [P1] `w_groove` rewards the wrong physical volume

The prompt prescribes a liquid volume of 1 and omits the sloping solid substrate. The reference defines energy integrals but no content integrals, then constrains the default body volume to `target_vol`: [wall definitions](/Users/yannhenon/code/surface-evolver-llm-eval/ground_truth_fe/w_groove.fe:83), [body definition](/Users/yannhenon/code/surface-evolver-llm-eval/ground_truth_fe/w_groove.fe:299).

The omitted walls are below z = 0 and have nonzero vertical flux. Consequently, the default free-surface integral does not measure the complete liquid volume. Evolver documents that its default volume is the facet integral of z dx dy, plus constraint content integrals and any volume constant. [Official body-volume documentation](https://kenbrakke.com/evolver/html/elements.htm).

I independently measured volume by integrating x n_x over the free surface. The omitted substrate is extruded along x, so its contribution to this alternative closed-surface flux is exactly zero. The added quantity is `info_only`; it does not change the minimization.

| State | Default `body[1].volume` | Independent geometric volume |
|---|---:|---:|
| Reference starting mesh | 3 | 4 |
| After prescribed `gogo` | 1 | 1.867242488127 |

The initial discrepancy also has a direct geometric check: the rectangular region above the ridges has volume 2 × 2 × 0.75 = 3; the two triangular grooves add 2 × (1 × 0.5 / 2) × 2 = 1.

**Impact:** The published area and energy targets describe a solution to the wrong volume constraint. A solver that correctly restores the omitted substrate's volume is solving a different optimization problem and should not be judged against these targets. The missing contribution changes as the contact line moves, so a single constant correction is insufficient.

**Repair:** Add consistent substrate content integrals or an equivalent physical volume formulation, independently verify the closed volume, then regenerate both numerical targets. State this volume requirement explicitly in the prompt. Do not merely widen tolerances around the current answer.

### 2. [P1] `cross_slot` grades an unspecified constant energy offset

The [energy expectation](/Users/yannhenon/code/surface-evolver-llm-eval/tasks_audit/cross_slot.json:98) is 0.511448402870516 ± 0.05. The matching reference with the prescribed `gogo` produces 0.3864484028705155. The discrepancy is **0.125**, or 2.5 times the tolerance. Area and volume match their expectations.

Follow-up inspection of historical passing submissions identifies the discrepancy. Both passing files in the saved `runs/` results use separate bottom integrals for the two arms, proportional to `WALLT*(x-HW)` and `-WALLT*(y-HW)`. These exclude the always-wetted central quarter-square. The current reference includes that square, whose energy is `WALLT*HW^2 = -0.125`. For this fixed wetting topology, the two functionals differ by a constant and produce the same equilibrium; neither the observed difference nor the reference failure means the task is impossible to pass.

Both historical passes reproduce against the current audit task. Adding the constant `WALLT*HW^2` to one of those passing submissions gives energy 0.386448402870516, area 1.280327459527907, and volume 0.375, matching the reference. A saved Gemini 3.8 Flash submission also has the reference's area and energy and fails solely on the energy offset. This makes the fairness issue concrete: the checker distinguishes physically equivalent energy conventions without specifying which convention to use.

**Repair:** Specify and normalize the energy zero convention, or compare invariant energy differences together with geometry and convergence. If reporting all wetted-solid energy, include the central square and use the corresponding target. Add an automated reference check. The origin of the task/reference divergence cannot be reconstructed from Git: these inputs are ignored and untracked.

### 3. [P1] Literal substring requirements reject valid equivalent datafiles

[Static checking](/Users/yannhenon/code/surface-evolver-llm-eval/src/se_eval/static_checks.py:89) strips comments and lowercases text, but does not normalize whitespace, parse expressions, or resolve syntax aliases. A static failure prevents a pass and removes 0.3 from the score even when all dynamic checks pass: [grading](/Users/yannhenon/code/surface-evolver-llm-eval/src/se_eval/grader.py:21).

Confirmed examples:

| Mutation to a passing reference | Evolver/dynamic result | Static result |
|---|---|---|
| Cube: `faces` → `facets` | Pass; volume 1, area 6 | Fails required `faces` |
| Cube: `volume 1` → `volume    1` | Pass; same measurements | Fails required `volume 1` |
| Cube: `volume 1` → `volume (1)` | Pass; same measurements | Fails required `volume 1` |
| Three plates: `cos(angle1*pi/180)` → `cos(pi*angle1/180)` | Pass; same measurements | Fails required cosine substring |

The last case directly contradicts the prompt's allowance of equivalent definitions. The `facets` case also contradicts the section counter's own explicit alias support.

Six tasks require the literal `faces` token: cube, pyramid, square well, three plates, parallel rods, and crossed fibers. Pyramid and three plates additionally require literal constraint formulas. Parameter declarations and `volume target_vol` requirements have similar whitespace sensitivity. Pyramid and parallel rods also impose numeric constraint IDs that their prose does not explicitly require; named or renumbered constraints can represent the same model.

**Repair:** Use Evolver's parsed model to check geometry, body targets, constraints, and parameter values. Remove expression-text requirements. If a lexical check remains, tokenize it and support valid aliases and whitespace. Preserve genuinely specified IDs such as body 1 and constraint IDs referenced by a supplied command.

### 4. [P1] Aggregate metrics do not enforce the requested geometry or body count

Confirmed full-pass counterexamples for `cube`:

- Translate all vertices by +10 along x. The cube now occupies [10,11] × [0,1] × [0,1], contrary to the requested coordinates; it still scores 1.0.
- Append a second body using the oppositely oriented faces and target volume −1. Evolver accepts the datafile, and the grader still scores 1.0 despite the explicit requirement for exactly one body. This is a probe of the missing count check, not a recommended physical model.

All tasks use `min_bodies: 1` and require ID 1; none checks the exact count. Their dynamic checks inspect parameter values, body volume, and a few global scalars. They do not inspect whether parameters actually define the geometry, whether contact loops are attached to the required surfaces, whether the mesh is connected, or whether forbidden solid patches belong to the body. The cube counterexamples prove the gap; the other omissions follow from the check definitions and were not each tested with a constructed exploit.

**Repair:** Add exact body count, `body[1].volfixed` and target checks, geometric residuals, contact membership/topology checks, and physical-domain checks. For cube, verify the occupied unit-cube boundary and orientation while allowing legitimate triangulation. For droplets, distinguish free-surface facets from substrate/display facets. Inspect relevant invariants before and after evolution.

### 5. [P1] Longer evolution can crash grading instead of producing a timeout result

The dynamic checker imposes an undisclosed, fixed ten-second timeout: [checker constructor](/Users/yannhenon/code/surface-evolver-llm-eval/src/se_eval/dynamic_checks.py:24). Appending `g 500; r; u; g 500;` to the parallel-rod reference's user-defined evolution exceeded it locally and raised:

```text
TypeError: cannot use a string pattern on a bytes-like object
```

The subprocess timeout path returns captured bytes without decoding them: [timeout handler](/Users/yannhenon/code/surface-evolver-llm-eval/src/se_eval/evolver.py:93). The metric parser then applies a string regular expression to those bytes. A separate short, bounded timeout probe reproduces the exception.

**Impact:** A reasonable attempt to satisfy “continues evolving to convergence” can become a grading exception. Runtime also depends on mesh resolution and hardware; reference runtimes here ranged from hundredths of a second to roughly two seconds, which does not establish a fair limit for all valid submissions.

**Repair:** Decode captured output consistently, return a structured timeout failure, disclose a calibrated resource budget, and make it configurable per task. Set a measurable convergence criterion for tasks that let the solver choose the evolution procedure.

### 6. [P2] `pyramid_mound` has an under-evolved reference and no explicit stopping criterion

The matching reference fails the [energy target](/Users/yannhenon/code/surface-evolver-llm-eval/tasks_audit/pyramid_mound.json:56): 4.165328195716 versus 4.079111342822 ± 0.05. Its area remains inside the looser ±0.1 band, and its volume is correct.

Appending `g 500; r; u; g 500;` inside `gogo` gives energy 4.099808072190 and area 3.929222857074, making the same geometry pass. This supports inadequate evolution/resolution as an explanation; it does not prove the target is the continuum limit.

**Repair:** Replace the reference with one that actually passes, document how the target was converged, and specify a residual/energy-change criterion or a complete reproducible finite evolution setup. The supplied starting apex height is currently unspecified. Also align the public and hidden scripts: only the hidden script prepends `G 0`; the prompt should explicitly request zero gravity if that is part of the physical model.

### 7. [P2] Suggested meshes are treated as mandatory, but fixed recipes lack complete initial conditions

Most prompts describe “a simple valid starting geometry” while imposing minimum vertex/edge/face counts taken from that construction. These counts can penalize a valid coarser or differently organized mesh; for example, the W task requires 14 vertices even though its 14-vertex box construction is presented as an example, not a mandatory mesh. The audit has not constructed and converged every such alternative, so these are specification risks rather than demonstrated numerical false negatives.

The five tasks with exact prescribed `gogo` commands still leave choices in triangulation, contact-loop placement/connectivity, or boundary treatment. Executing the same finite list of gradient steps does not define a mesh-independent equilibrium. Conversely, the static checks only search for fragments of those commands and do not verify their sequence or completeness.

**Repair:** Choose and state the assessment objective. For a finite-trajectory reproduction task, supply complete initial coordinates/connectivity and the numerical settings needed for reproducibility. For a modeling task, allow equivalent discretizations and evolution procedures, then assess geometry, physical functionals, and convergence. Keep only structurally justified minimum counts.

### 8. [P2] The no-execution-on-load requirement is incompletely enforced

Appending `read` followed by `recalc` to the cube reference executes a command on load and still passes all checks. [Command hygiene](/Users/yannhenon/code/surface-evolver-llm-eval/src/se_eval/fe_hygiene.py:69) uses an incomplete command-prefix list and skips a whole line whenever it contains `:=`; it is not a parser for command definitions versus invocations.

**Repair:** Parse the post-`read` portion sufficiently to allow definitions and reject executable top-level statements, including invocations of arbitrary user-defined commands. Retain execution isolation separately from this benchmark-conformance check.

## Geometry and specification review, task by task

These clarifications are additional to the confirmed findings above. They should make a valid physical solution identifiable without access to the reference implementation.

### `cube`

The geometry is the clearest in the set. State that all eight corners of [0,1]^3 are intended and that triangulated faces are acceptable. Do not require a literal quadrilateral `faces` representation. Verify placement and outward orientation, exact body count, and prescribed volume. Fixed versus mobile vertices does not matter for the current non-evolving test.

### `pyramid_mound`

The four equations specify infinite planes, not bounded pyramid faces. State the substrate envelope `z = -slope*(abs(x)+abs(y))`, the quadrant domain of each face, and that the solid lies below it. Say whether the pyramid is effectively unbounded below the apex or has a finite base outside the modeled region. Make explicit that ridge contacts may slide along their ridge rays and that the contact line remains around the apex. The current two-plane constraints define entire intersection lines, including extensions that are not the intended ridge rays.

The prompt appropriately requests substrate volume corrections and the face-area scale factor. Keep those physical requirements, while accepting equivalent integral formulations. Explain unit free-surface tension and zero gravity. Specify initialization only as strictly as the convergence test requires.

### `square_well`

The horizontal walls are well located, but no bottom plane or wall height is specified. State that the bottom is z = 0, liquid lies above it and within 0 ≤ x,y ≤ AA, and the vertical walls extend above the initial level. Clarify that AA is the **initial fill height**, not a rim that pins the contact line. With a wetting meniscus, a finite rim at z = AA would define a different problem.

State that the contact line slides vertically, corner contacts remain on both adjacent walls, all four walls share the interior-liquid angle, and omitted-wall energy is measured relative to dry walls from the bottom datum. Require tension `TENS` on the free surface and density 1 semantically; printing their parameter names is not enough. Once the bottom datum is explicit, vertical walls and a z = 0 bottom need no correction to the default z-based volume integral.

### `cross_slot`

The union of grooves, first-quadrant footprint, and quarter-volume convention are substantially clearer than in most other tasks. State the bottom explicitly as x3 = 0, specify effectively unbounded wall height, and restrict side-wall patches to their physical arm domains. Symmetry boundaries should carry no solid-contact energy and represent a freely meeting reflected surface. State how the contact line treats the vertical corner at (HW,HW) and the wall-bottom intersections.

The supplied `MIDARM`, endpoint heights, and “six triangles” do not give a complete vertex/constraint/connectivity table. Provide that table if the exact finite trajectory is required. Ensure the central quarter-square's bottom energy is counted once; repair the current target mismatch first. Clearly label area and energy as quarter-domain values alongside the quarter-volume check.

### `bridge_three_plates`

The normals and plane positions are precise. State that the liquid lies in the central intersection `n_i·(x,y,0) <= plate_r`, the planes act as effectively unbounded walls, and the three contact loops remain distinct and mobile. Define local tangents and the initial rectangle centers `(plate_r*n_i.x, plate_r*n_i.y,z_mid)` if the finite evolution recipe is the test. A half-width and half-height alone do not completely locate a rectangle on an infinite plane.

Clarify whether contact loops may reach the intersections between plates, and what happens then. “Liquid bridge or bubble” should be resolved to one energy/phase convention, or explicitly state that both mean the same unit-tension, fixed-volume interface model here. The algebraic formulations already permitted by the prompt must be accepted by grading.

### `bridge_two_rods`

Radius, separation, and parallel z axes are well specified. Explicitly state unit liquid-air tension, exterior-of-both-cylinders admissibility, mobile inward-facing contact patches, and a single connected bridge without wrapping or pinch-off during the prescribed wetting state. Say that the initial patches are centered at z = 0 if that matters to reproducibility.

There is no operational definition of “convergence”: no residual, maximum refinement, iteration budget, or stated numerical tolerance. The prompt asks for mesh-quality operations “where needed,” so avoid prescribing a particular operation through incidental source text. `theta_half` and `z_half` are required text but, unlike the crossed-fiber task, are not checked as dynamic default values.

The z-parallel cylinder orientation correctly makes the omitted patches' default z-volume flux vanish. Requiring `convex` has a numerical consequence: Evolver adds a mesh-dependent gap energy. Make its role and coefficient explicit if `total_energy` is compared numerically. [Official gap-energy documentation](https://kenbrakke.com/evolver/html/energies.htm).

### `fiber_bridge_crossed`

The two axes are mutually perpendicular but spatially separated: “crossed” refers to their projection, not intersecting centerlines. The equations and spacing define this adequately; a sentence on the nearest surface gap would remove doubt.

The key missing requirement is the volume correction for the x-parallel cylinder. The prompt discusses contact energy but does not mention restoring the omitted patch's volume, while the static checks silently require `content:`. The reference itself explains the need and its atan2 branch choice: [derivation](/Users/yannhenon/code/surface-evolver-llm-eval/ground_truth_fe/fiber_bridge_crossed.fe:15). Add that physical requirement to the prompt and accept an equivalent volume formulation; the literal keyword alone neither proves nor exhausts correctness.

Give an untwisted correspondence between the two four-vertex loops if the exact provided evolution path matters. State that contact patches stay on the inward-facing branches, avoid a cylindrical-coordinate branch cut, and cannot penetrate either solid. Include the same gap-energy convention as the parallel-rod task.

### `w_groove`

The W profile and explicitly prescribed two-groove wetting state are useful and should be retained. The main blocker is the missing physical volume described in finding 1.

Clarify what “pinned” means: the outer contact curves are constrained to ridge **lines**, but their vertices may move along x; this does not necessarily fix their material positions or endpoints. State that `x_left` and `x_right` locate the initial end curves, not permanent end planes, and that inner ridge/valley crossings can slide along x. Distinguish this from an entirely fixed contact perimeter, which gives different equilibria.

Specify each sloping plane's physical y interval, how end contact curves remain on those intervals, and that auxiliary neighboring planes contribute no extra physical wetted area. The reference applies `below_ridge` to the contact edges and pins ridge/valley crossing vertices using additional constraints; those state restrictions are not fully described in the prompt. Do not apply the Young angle as an extra hard condition at deliberately pinned ridge contacts; state it as the wall wetting-energy coefficient.

## Recommended repair order

1. Correct W-groove physical volume and regenerate its reference/targets. Reconcile cross-slot energy and replace the failing pyramid reference.
2. Add a reference-suite check: every reference must load, obey the prompt, pass its task, and satisfy an independent physical volume/energy sanity check. Passing its own scalars alone is insufficient.
3. Remove representation-sensitive substring gates; add equivalent-syntax and geometry-negative probes based on the confirmed examples above.
4. Add exact body count, volume-target state, contact geometry, solid exclusion, and wetting-topology checks. Validate default parameters before evolution as well as the resulting state afterward; currently all hidden metrics run after `gogo`.
5. Define whether each task tests physical equilibrium or an exact finite evolution trajectory. Calibrate tolerances using independent discretizations and further refinement, and publish operational stopping/resource requirements without needing to publish the answers.
6. Fix timeout handling and command hygiene. Then rerun the affected benchmark evaluations; earlier pass/fail results can reflect these defects rather than modeling ability.

## Reproduction and limits

### Historical-pass follow-up

The saved `runs/` directory contains 25 result records for each task: two `cross_slot` passes and five `w_groove` passes. All seven reproduce as passes against the audit tasks. These counts describe the available records, not every experiment ever run. [Historical rerun evidence](/Users/yannhenon/code/surface-evolver-llm-eval/docs/audits/2026-09-18-tasks-audit/historical_evidence.json).

The two cross-slot passes are Claude Fable 5 and GPT-5.6 Sol xhigh; they use the central-square-excluding energy convention described above. The five W-groove passes are Claude Fable 5, GPT-5.5, GPT-5.6 Sol xhigh, GPT-5.6 Terra xhigh, and Kimi K3. All five omit substrate content integrals, and the independent x-flux measurement gives physical volumes between **1.867474555395 and 1.867494800345** while their checked body volume is 1. Their passes are therefore consistent with the reference's volume-model defect.

The private and audit cross-slot task definitions are identical. For W-groove, the only private/audit difference is area/energy tolerance: 0.01 in private versus 0.05 in audit. The historical passing submissions are well inside both tolerances, so that difference does not explain the issue.

The earlier description of cross-slot as a reference/target inconsistency was accurate but incomplete: it is specifically an additive energy convention mismatch, unlike the W-groove physical-volume error.

### Initial audit probes

Run from the repository root:

```sh
PYTHONPATH=src .venv/bin/python docs/audits/2026-09-18-tasks-audit/probe.py
```

This records all eight baseline grades, harmless equivalence mutations, incorrect-cube counterexamples, additional evolution, independent W-groove volume, and bounded timeout handling. The original audit also checked an extra 500 gradient steps without refinement on the parallel rods: energy decreased from 4.744563962995 to 4.743604079999 and area changed from 5.439578887871 to 5.450670893499, both within tolerance. This is **not** evidence that the rod target is invalid; it illustrates why finite-step output should be distinguished from a certified limit.

This audit does not certify all eight continuum equilibria, perform a full stability/bifurcation analysis, or prove that every possible alternative discretization is accepted or rejected. Confirmed defects are separated from proposed specification improvements for that reason. Runtime observations are machine-dependent. Input hashes in the evidence identify exactly which task/reference versions were tested.
