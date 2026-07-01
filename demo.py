"""Demo script: Run the full Spark pipeline with sample data.

This demonstrates the complete literature-to-idea pipeline:
1. Create sample papers (simulating literature processing)
2. Build knowledge graph
3. Mine research patterns
4. Discover research gaps
5. Assess feasibility
6. Score innovations
7. Generate proposals
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.models import (
    PaperMetadata,
    ResearchPattern,
    StudyType,
    EvidenceLevel,
)
from src.core.storage import InMemoryStorage
from src.literature.processor import LiteratureProcessor
from src.knowledge_graph.builder import KnowledgeGraph
from src.pattern_mining.miner import PatternMiner
from src.gap_discovery.engine import GapDiscoveryEngine
from src.feasibility.assessor import FeasibilityAssessor
from src.scoring.engine import InnovationScorer
from src.proposal.generator import ProposalGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("spark_demo")


def create_sample_papers() -> list[PaperMetadata]:
    """Create realistic sample papers for demonstration."""
    return [
        PaperMetadata(
            pmid="35000001",
            title="Association between albumin infusion and mortality in sepsis patients",
            journal="Critical Care Medicine",
            publication_year=2023,
            study_type=StudyType.COHORT,
            population="sepsis",
            exposure="albumin",
            outcome="mortality",
            covariates=["age", "SOFA", "creatinine"],
            statistical_methods=["IPTW", "propensity_score_matching"],
            main_findings=["Albumin infusion associated with reduced mortality in sepsis"],
            keywords=["sepsis", "albumin", "mortality", "fluid_resuscitation"],
            evidence_level=EvidenceLevel.LEVEL_2,
        ),
        PaperMetadata(
            pmid="35000002",
            title="Albumin variability and acute kidney injury in critically ill patients",
            journal="Intensive Care Medicine",
            publication_year=2023,
            study_type=StudyType.CAUSAL_INFERENCE,
            population="sepsis",
            exposure="albumin_variability",
            outcome="acute_kidney_injury",
            covariates=["age", "baseline_creatinine"],
            statistical_methods=["linear_regression", "mixed_effects"],
            main_findings=["Higher albumin variability associated with increased AKI risk"],
            keywords=["sepsis", "albumin", "AKI", "variability"],
            evidence_level=EvidenceLevel.LEVEL_2,
        ),
        PaperMetadata(
            pmid="35000003",
            title="Crystalloid vs colloid resuscitation in trauma patients",
            journal="Annals of Surgery",
            publication_year=2022,
            study_type=StudyType.RCT,
            population="trauma",
            exposure="crystalloid",
            outcome="mortality",
            covariates=["age", "ISS", "SBP"],
            statistical_methods=["logistic_regression"],
            main_findings=["No significant difference in mortality between crystalloid and colloid"],
            keywords=["trauma", "fluid_resuscitation", "mortality"],
            evidence_level=EvidenceLevel.LEVEL_1,
        ),
        PaperMetadata(
            pmid="35000004",
            title="Predictors of 90-day mortality in ARDS patients",
            journal="American Journal of Respiratory and Critical Care Medicine",
            publication_year=2023,
            study_type=StudyType.COHORT,
            population="acute_respiratory_distress_syndrome",
            exposure=None,
            outcome="mortality_90",
            covariates=["age", "PaO2/FiO2", "SOFA", "BMI"],
            statistical_methods=["cox_proportional_hazards"],
            main_findings=["Low PaO2/FiO2 and high SOFA predict 90-day mortality"],
            keywords=["ARDS", "mortality", "predictors", "PaO2/FiO2"],
            evidence_level=EvidenceLevel.LEVEL_2,
        ),
        PaperMetadata(
            pmid="35000005",
            title="Vasopressor duration and organ dysfunction in septic shock",
            journal="Critical Care",
            publication_year=2024,
            study_type=StudyType.COHORT,
            population="sepsis",
            exposure="vasopressor_duration",
            outcome="organ_dysfunction",
            covariates=["age", "SOFA", "lactate"],
            statistical_methods=["multivariable_regression", "spline"],
            main_findings=["Longer vasopressor duration associated with worse organ recovery"],
            keywords=["sepsis", "vasopressors", "organ_dysfunction", "SHOCK"],
            evidence_level=EvidenceLevel.LEVEL_2,
        ),
        PaperMetadata(
            pmid="35000006",
            title="Early goal-directed therapy in congestive heart failure exacerbation",
            journal="European Heart Journal",
            publication_year=2022,
            study_type=StudyType.CROSS_SECTIONAL,
            population="congestive_heart_failure",
            exposure="fluid_management",
            outcome="rehospitalization",
            covariates=["age", "LVEF", "BNP"],
            statistical_methods=["logistic_regression"],
            main_findings=["Aggressive fluid management associated with higher rehospitalization"],
            keywords=["CHF", "fluid_management", "rehospitalization"],
            evidence_level=EvidenceLevel.LEVEL_3,
        ),
        PaperMetadata(
            pmid="35000007",
            title="Biomarker panels for early sepsis detection in the ICU",
            journal="JAMA",
            publication_year=2024,
            study_type=StudyType.PREDICTIVE_MODEL,
            population="sepsis",
            exposure="biomarker_panel",
            outcome="early_detection",
            covariates=["age", "qSOFA", "lactate"],
            statistical_methods=["random_forest", "XGBoost", "AUC_calibration"],
            main_findings=["Combined biomarker panel improves early sepsis detection (AUC 0.89)"],
            keywords=["sepsis", "biomarkers", "machine_learning", "early_detection"],
            evidence_level=EvidenceLevel.LEVEL_2,
        ),
        PaperMetadata(
            pmid="35000008",
            title="Renal replacement therapy timing in AKI: a systematic review",
            journal="Intensive Care Medicine",
            publication_year=2023,
            study_type=StudyType.SYSTEMATIC_REVIEW,
            population="acute_kidney_injury",
            exposure="RRT_timing",
            outcome="mortality",
            covariates=["age", "SOFA", "dialysis_dependence"],
            statistical_methods=["meta_analysis"],
            main_findings=["Early RRT shows trend toward reduced mortality but evidence is inconclusive"],
            keywords=["AKI", "RRT", "timing", "meta_analysis"],
            evidence_level=EvidenceLevel.LEVEL_1,
        ),
    ]


def run_demo() -> None:
    """Execute the full pipeline demonstration."""
    logger.info("=" * 60)
    logger.info("Spark Research Discovery Platform - Demo")
    logger.info("=" * 60)

    # Initialize components
    storage = InMemoryStorage()
    kg = KnowledgeGraph()
    miner = PatternMiner()
    gap_engine = GapDiscoveryEngine()
    assessor = FeasibilityAssessor()
    scorer = InnovationScorer()
    proposer = ProposalGenerator()

    # ── Step 1: Load literature ───────────────────────────────────────
    logger.info("\n[1/7] Loading sample literature...")
    papers = create_sample_papers()
    logger.info("Loaded %d papers", len(papers))

    for paper in papers:
        storage.save_paper(paper)
        kg.add_paper(paper)

    # ── Step 2: Mine patterns ─────────────────────────────────────────
    logger.info("\n[2/7] Mining research patterns...")
    patterns = miner.mine_from_papers(papers)
    patterns = miner.deduplicate_patterns(patterns)
    for p in patterns:
        miner.register_pattern(p)
        kg.add_pattern(p)
    logger.info("Mined %d unique patterns", len(patterns))

    popular = miner.get_popular_patterns()
    if popular:
        logger.info("Most studied pattern: %s (%dx)",
                     popular[0].population, popular[0].frequency)

    # ── Step 3: Build knowledge graph ─────────────────────────────────
    logger.info("\n[3/7] Building knowledge graph...")
    stats = kg.get_statistics()
    logger.info("Graph: %d nodes, %d edges, %d components",
                 stats["total_nodes"], stats["total_edges"],
                 stats["connected_components"])

    # ── Step 4: Discover gaps ─────────────────────────────────────────
    logger.info("\n[4/7] Discovering research gaps...")
    known = set()
    for p in patterns:
        if p.exposure and p.outcome and p.population:
            known.add((p.population, p.exposure, p.outcome))
    ideas = gap_engine.discover_gaps(patterns, known)
    logger.info("Discovered %d research ideas", len(ideas))

    # ── Step 5: Assess feasibility ────────────────────────────────────
    logger.info("\n[5/7] Assessing feasibility...")
    for idea in ideas:
        assessor.assess_idea(idea)
    feasible = [i for i in ideas if i.feasibility_score and i.feasibility_score > 0.3]
    logger.info("%d ideas are feasible (score > 0.3)", len(feasible))

    # ── Step 6: Score innovations ─────────────────────────────────────
    logger.info("\n[6/7] Scoring innovation...")
    scored = scorer.score_batch(ideas)
    dist = scorer.get_score_distribution(ideas)
    logger.info("Score distribution: mean=%.3f, median=%.3f, max=%.3f",
                 dist["mean"], dist["median"], dist["max"])

    # ── Step 7: Generate proposals ────────────────────────────────────
    logger.info("\n[7/7] Generating proposals...")
    top_ideas = sorted(
        [i for i in ideas if i.overall_score],
        key=lambda x: x.overall_score,
        reverse=True,
    )[:3]
    proposals = proposer.generate_batch(top_ideas)

    # ── Print results ─────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("TOP RESEARCH IDEAS")
    logger.info("=" * 60)
    for i, idea in enumerate(top_ideas, 1):
        logger.info("\n#%d. %s", i, idea.title)
        logger.info("   Population: %s", idea.population)
        logger.info("   Exposure: %s", idea.exposure)
        logger.info("   Outcome: %s", idea.outcome or "N/A")
        logger.info("   Feasibility: %.2f", idea.feasibility_score or 0)
        logger.info("   Innovation: %.2f", idea.overall_score or 0)

    logger.info("\n" + "=" * 60)
    logger.info("GENERATED PROPOSALS")
    logger.info("=" * 60)
    for prop in proposals:
        output = proposer.export_proposal(prop)
        logger.info("\n%s", output[:500])

    logger.info("\n" + "=" * 60)
    logger.info("Demo complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_demo()