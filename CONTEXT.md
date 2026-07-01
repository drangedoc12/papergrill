# Spark — Domain Language

## What is Spark?

Spark is an AI-driven **Research Idea Discovery Platform** for critical-care databases (MIMIC-IV, eICU). It ingests biomedical literature, extracts PICO-structured metadata, builds a knowledge graph, mines research patterns, discovers novel gap-driven research ideas, assesses feasibility, scores innovation, and generates publication-ready proposals.

## Core pipeline (7 stages)

```
Literature → Knowledge Graph → Pattern Mining → Gap Discovery → Feasibility → Scoring → Proposal
```

| Stage | Module | Responsibility |
|---|---|---|
| Literature | `src/literature/` | Parse PDFs (PyMuPDF) and PubMed XML → `PaperMetadata` (PICO) |
| Graph | `src/knowledge_graph/` | NetworkX MultiGraph: entity nodes (disease, biomarker, outcome, treatment) + paper nodes + pattern edges |
| Mining | `src/pattern_mining/` | Extract `ResearchPattern` objects from papers, deduplicate, build exposure-outcome co-occurrence matrix |
| Gaps | `src/gap_discovery/` | 6 strategies (see below) → `ResearchIdea` objects |
| Feasibility | `src/feasibility/` | Check MIMIC-IV/eICU variable availability, cohort size, SQL complexity |
| Scoring | `src/scoring/` | 5-dimension weighted scoring (novelty, clinical importance, DB availability, stat feasibility, publication potential) |
| Proposals | `src/proposal/` | Generate full `ResearchProposal` per idea category |

## Domain model

### PaperMetadata (PICO+)

| Term | Definition | Example |
|---|---|---|
| **Population** | The study cohort or disease focus | `sepsis`, `sepsis-associated AKI`, `sepsis with cancer`, `stroke (ischemic/hemorrhagic)`, `PICU children` |
| **Exposure** | The predictor, intervention, or risk factor being studied | `serum phosphate trajectory`, `TyG index`, `EASIX`, `Charlson Comorbidity Index (CCI)`, `laxative type` |
| **Outcome** | The endpoint measured | `28-day mortality`, `AKI incidence`, `NOAF` |
| **ExposureType** | How the exposure is measured | `static_single_measure`, `dynamic_trajectory`, `variability`, `cumulative`, `composite_index` |
| **OutcomeCategory** | Outcome taxonomy | `mortality`, `organ_dysfunction`, `resource_use`, `recurrent_event`, `composite` |

### Gap strategies

| Gap strategy | Definition | Example |
|---|---|---|
| **matrix_gap** | An (population, exposure, outcome) combination absent from the literature | AIP (exposure) → AKI (outcome) in sepsis (population) |
| **static_to_dynamic** | A known static exposure that can be upgraded to trajectory/variability/cumulative analysis using MIMIC-IV time-series | EASIX at admission (static) → EASIX trajectory over 72h (dynamic) |
| **subpopulation** | Re-analyse a known association in a specific unstudied subgroup | TyG → mortality in elderly sepsis patients |
| **refined_outcome** | Replace a crude outcome with a granular/cause-specific endpoint | Hospital mortality → cause-specific mortality (CV vs non-CV) using competing risk |
| **understudied** | A population with <3 papers in the current corpus | Sepsis + ECMO |
| **cross_disease** | A statistical method validated in one population but not yet applied to another | LGMM trajectory from sepsis → applied to ARDS |

### Edge types in knowledge graph

| Edge | Meaning |
|---|---|
| `studies` | Paper → Population |
| `measures` | Paper → Exposure (with exposure_type) |
| `evaluates` | Paper → Outcome (with outcome_category) |
| `uses_method` | Paper → StatisticalMethod |
| `adjusts_for` | Paper → Covariate |
| `associated_with` | Exposure → Outcome (with frequency, pattern_id) |
| `co_occurs` | Exposure ↔ Exposure (appear together in ≥1 paper) |

## Block folders (pubmed/)

Papers are organised into 6 thematic blocks under `pubmed/`, plus uncatalogued papers in root:

| Block | Focus | Count |
|---|---|---|
| `01_biomarker` | Novel biomarker-outcome associations (TyG, LAR, EASIX, AIP, SHRs, ePVS, CAR, SGPR, PIV) | 10 |
| `02_trajectory` | Dynamic trajectory modelling (phosphate, NLPR, BUN, FiO₂) | 4 |
| `03_subpopulation` | Specific sepsis complications / subgroups (NOAF, ICU infections, ECMO/CRRT, SAE, obesity) | 6 |
| `04_treatment` | Treatment/intervention evaluation (laxatives, Ramelteon, dexmedetomidine, KDIGO, antibiotics, HFNC, CPAP, enteral nutrition) | 11 (including 0007, 0046, 0047) |
| `05_prediction_model` | ML/nomogram predictive models (cancer+sepsis, SALI, TBI, SATP, delirium, SOFA) | 6 |
| `06_refined_outcome` | Granular outcome definitions (ARDS, SA-AKI mortality, AKI incidence, dual outcomes, ARDS definition) | 4 |
| `(uncatalogued)` | Root analyses: 0045 (stroke + CCI) | 1 |

## Paper Review: 八维解读框架 (8-Dimension Framework)

Every paper in the Spark corpus should be analysed along these 8 dimensions, plus a bottom-line quality assessment.

### Eight dimensions

| # | Dimension | Key questions |
|---|---|---|
| **1** | **基本信息定位** | 期刊、作者、发表时间、研究类型（RCT/队列/荟萃） |
| **2** | **研究背景与临床痛点** | 为什么做？解决什么临床问题？现有证据的gap在哪？ |
| **3** | **方法学质量评估** | 设计是否合理？偏倚风险（selection/information/confounding）? 样本量是否充分？ |
| **4** | **统计学分析深度解读** | 模型选择是否恰当？假设检验方法？效应量（HR/OR/ATE）及其含义？ |
| **5** | **主要结果呈现与证据强度** | 核心发现是什么？置信区间宽度？证据等级（OCEBM）？ |
| **6** | **关键图表精读** | 不只看结论，看数据怎么支撑结论——KM曲线分离度、RCS形状、亚组森林图的一致性 |
| **7** | **临床意义与实践启示** | 对床旁决策意味着什么？NNT/NNH？能否改变临床路径？ |
| **8** | **局限性与未来研究方向** | 不可靠的地方在哪？残余混杂？外部有效性？还能怎么挖（→ gap strategies）？ |

### Quality assessment: 三问底层检验

Every analysis must conclude with these three questions:

1. **结果是真的吗？** — 内部有效性：偏倚控制、混淆调整、敏感性分析是否充分
2. **重要吗？** — 效应量大小、临床相关性：HR 1.05 vs 2.50 本质区别
3. **对我有用吗？** — 外部有效性：MIMIC-IV → 我自己的ICU/人群是否适用

### Integration with pipeline stages

| Pipeline stage | How the framework applies |
|---|---|
| `src/literature/` | D1-D2 (basic info, background) → populate `PaperMetadata`; D3-D4 (method, stats) → populate `exposure_type`, `statistical_methods`, quality flags |
| `src/pattern_mining/` | D5-D6 (results, figures) → extract `ResearchPattern.effect_size`, `ResearchPattern.key_finding` |
| `src/gap_discovery/` | D8 (limitations, future) → seed `ResearchIdea.rationale`, map to gap strategies |
| `src/scoring/` | D7 (clinical impact) + 三问 → inform innovation/feasibility scoring |

## Used terminology

- **Gap**: A missing (population, exposure, outcome) triple in the co-occurrence matrix, or a methodological upgrade opportunity
- **Pattern**: A recurring (population, exposure, outcome) association with statistical method, covariates, frequency
- **Feasibility**: Whether a research idea can be executed on MIMIC-IV / eICU given variable availability and cohort size
- **Proposal**: A publication-ready research plan with population definition, SAP, variable mapping, expected impact
- **Idea category**: The kind of gap an idea fills (one of matrix_gap, static_to_dynamic, subpopulation, refined_outcome)
