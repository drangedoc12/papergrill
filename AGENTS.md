# Agent configuration for Spark

Spark is an AI-driven Research Idea Discovery Platform — it ingests critical-care literature (PubMed PDFs), builds a PICO-structured knowledge graph, mines research patterns, discovers novel gap-driven research ideas, assesses feasibility on MIMIC-IV/eICU, scores innovation, and generates publication-ready proposals.

## Agent skills

### Issue tracker

Local markdown — issues and PRDs live as files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical roles with default names. See `docs/agents/triage-labels.md`.

| Role | Label |
|---|---|
| needs-triage | `needs-triage` |
| needs-info | `needs-info` |
| ready-for-agent | `ready-for-agent` |
| ready-for-human | `ready-for-human` |
| wontfix | `wontfix` |

### Domain docs

Single-context repo. `CONTEXT.md` at the root defines the domain language; `docs/adr/` captures architectural decisions. See `docs/agents/domain.md`.

---

## Skill integration with Spark

### Engineering skills

| Skill | When to use | Spark-specific behaviour |
|---|---|---|
| **`/grill-with-docs`** | Before any non-trivial code change — align on the research module you're about to touch, sharpen its scope, and update CONTEXT.md with domain terms | Will ask: which pipeline stage (literature → KG → miner → gap → feasibility → scoring → proposal)? What exposure/outcome types are involved? |
| **`/domain-modeling`** | Automatically fires when terminology is fuzzy; actively builds the Spark domain glossary (PICO, exposure_type, outcome_category, gap categories) into CONTEXT.md | Expects terms like `matrix_gap`, `static_to_dynamic`, `subpopulation`, `refined_outcome` as first-class domain concepts |
| **`/tdd`** | When implementing a new pipeline module or gap strategy — vertical slice through the full stack | Test through high-level seams: `GapDiscoveryEngine.discover_gaps()` should return expected gap types given known patterns; `PatternMiner.mine_from_papers()` should deduplicate correctly |
| **`/codebase-design`** | Model-invoked when designing module interfaces; applies deep-module vocabulary to pipeline stages | A `GapDiscoveryEngine` with a single `discover_gaps(patterns, known_set)` method is deep; avoid shallow pass-through wrappers |
| **`/prototype`** | When exploring a new gap strategy or scoring dimension — build a throwaway terminal app to interactively test the logic before committing to production code | Prototype exposes full internal state: `papers analyzed → embeddings → patterns → gaps found → scores` |
| **`/diagnosing-bugs`** | When a pipeline step fails or produces unexpected results (wrong gap detection, parser crash, KG missing edges) | Build tight feedback loop: a pytest feeding a known paper pair and asserting specific gap categories; minimise to smallest reproducing dataset |
| **`/review`** | Review code changes along two axes: Standards (module structure, Fowler smells) and Spec (does the code implement the research methodology correctly?) | Spec axis checks: are the gap strategies correctly implemented? Are exposure/outcome types inferred per the ontology? |
| **`/improve-codebase-architecture`** | Periodically (every few days of active dev) — scan for architectural friction and deepening opportunities | May flag: literature/ parser tangled with PDF I/O; gap_discovery/engine.py doing too many things |
| **`/handoff`** | End of session — compact the conversation into a handoff document so the next agent continues seamlessly | Includes: what pipeline stage was worked on, what ADRs were created, what's pending next |
| **`/to-prd`** | After `/grill-with-docs` — publish the agreed scope as a PRD to `.scratch/` | PRD uses research domain language: exposure/outcome/population triples, gap category, MIMIC-IV feasibility notes |
| **`/to-issues`** | After `/to-prd` — break the PRD into vertical-slice issues in `.scratch/<feature-slug>/issues/` | Each issue is a tracer bullet through all layers: schema change → parser change → KG update → pattern test |
| **`/triage`** | Process incoming issues through the label state machine | Issues use research domain vocabulary; triage labels are recorded as `Status:` lines in `.scratch/` files |

### Productivity skills

| Skill | When to use |
|---|---|
| **`/grill-me`** | Before making a non-code plan (research direction, paper outline, experiment design) |
| **`/teach`** | When you want to learn a new concept (e.g., causal inference methods, MIMIC-IV schema) interactively |

### Meta skill

| Skill | When to use |
|---|---|
| **`/writing-great-skills`** | Reference when creating custom Spark-specific skills |

---

## Project conventions

- **Pipeline entry point**: `run_pipeline.py` — end-to-end from pubmed PDFs to research proposals
- **All PDFs + analysis files**: `pubmed/` root + 6 block folders
- **Tests**: `tests/` with pytest
- **Config**: `config/settings.yaml`
- **Domain vocabulary**: `CONTEXT.md` — keep updated as new research terms emerge
- **Architectural decisions**: `docs/adr/` — write ADRs for any method choice (e.g., "why LGMM for trajectory modeling", "why NetworkX for KG")
