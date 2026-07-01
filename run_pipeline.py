"""End-to-end pipeline: parse PDFs from pubmed folder -> full discovery pipeline."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.storage import InMemoryStorage
from src.knowledge_graph.builder import KnowledgeGraph
from src.pattern_mining.miner import PatternMiner
from src.gap_discovery.engine import GapDiscoveryEngine
from src.feasibility.assessor import FeasibilityAssessor
from src.scoring.engine import InnovationScorer
from src.proposal.generator import ProposalGenerator
from src.literature.pdf_parser import PDFParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("spark_e2e")


def run_pipeline(pubmed_folder: str = "pubmed") -> dict:
    """Run the full pipeline on local PDF files."""
    logger.info("=" * 70)
    logger.info("SPARK RESEARCH DISCOVERY PLATFORM — End-to-End Pipeline")
    logger.info("Source: %s", pubmed_folder)
    logger.info("=" * 70)

    # ── Step 1: Parse PDFs ─────────────────────────────────────────────
    logger.info("\n[STEP 1/7] Parsing PDFs from: %s", pubmed_folder)
    parser = PDFParser()
    folder = Path(pubmed_folder)
    pdf_files = sorted(folder.glob("*.pdf")) + sorted(folder.glob("*/[0-9]*.pdf"))
    logger.info("Found %d PDF files", len(pdf_files))

    papers = []
    for pdf_file in pdf_files[:10]:  # Process first 10 for demo
        logger.info("  Parsing: %s", pdf_file.name)
        try:
            paper = parser.parse_pdf(pdf_file)
            papers.append(paper)
            logger.info("    Title: %s", paper.title[:80])
            logger.info("    Authors: %s", paper.authors[:3])
            logger.info("    Population: %s", paper.population or "(none)")
            logger.info("    Exposure: %s", paper.exposure or "(none)")
            logger.info("    Outcome: %s", paper.outcome or "(none)")
            logger.info("    Methods: %s", paper.statistical_methods)
            logger.info("    Covariates: %s", paper.covariates)
        except Exception as e:
            logger.warning("    Failed to parse %s: %s", pdf_file.name, e)

    logger.info("Successfully parsed %d papers", len(papers))

    if not papers:
        logger.error("No papers parsed. Exiting.")
        return {}

    # ── Step 2: Build knowledge graph ───────────────────────────────────
    logger.info("\n[STEP 2/7] Building knowledge graph...")
    storage = InMemoryStorage()
    kg = KnowledgeGraph()

    for paper in papers:
        storage.save_paper(paper)
        kg.add_paper(paper)

    stats = kg.get_statistics()
    logger.info("  Nodes: %d, Edges: %d, Components: %d",
                 stats["total_nodes"], stats["total_edges"],
                 stats["connected_components"])

    # ── Step 3: Mine research patterns ──────────────────────────────────
    logger.info("\n[STEP 3/7] Mining research patterns...")
    miner = PatternMiner()
    patterns = miner.mine_from_papers(papers)
    patterns = miner.deduplicate_patterns(patterns)
    for p in patterns:
        miner.register_pattern(p)
        kg.add_pattern(p)
    logger.info("  Mined %d unique patterns", len(patterns))

    for p in patterns[:10]:
        logger.info("  [%s] pop=%s exp=%s out=%s freq=%d",
                     p.pattern_id, p.population[:40],
                     p.exposure[:30] if p.exposure else "None",
                     p.outcome[:30] if p.outcome else "None",
                     p.frequency)

    # ── Step 4: Discover gaps ───────────────────────────────────────────
    logger.info("\n[STEP 4/7] Discovering research gaps...")
    gap_engine = GapDiscoveryEngine()
    known = set()
    for p in patterns:
        if p.exposure and p.outcome and p.population:
            known.add((p.population, p.exposure, p.outcome))
    ideas = gap_engine.discover_gaps(patterns, known)
    logger.info("  Discovered %d research ideas", len(ideas))

    # ── Step 5: Feasibility assessment ──────────────────────────────────
    logger.info("\n[STEP 5/7] Assessing feasibility...")
    assessor = FeasibilityAssessor()
    for idea in ideas:
        assessor.assess_idea(idea)
    feasible = [i for i in ideas if i.feasibility_score and i.feasibility_score > 0.3]
    logger.info("  Feasible ideas (score > 0.3): %d", len(feasible))

    # ── Step 6: Innovation scoring ──────────────────────────────────────
    logger.info("\n[STEP 6/7] Scoring innovations...")
    scorer = InnovationScorer()
    scored = scorer.score_batch(ideas)
    dist = scorer.get_score_distribution(ideas)
    logger.info("  Score distribution:")
    logger.info("    Mean: %.3f | Median: %.3f | Max: %.3f | Min: %.3f",
                 dist["mean"], dist["median"], dist["max"], dist["min"])

    # ── Step 7: Generate proposals for top ideas ────────────────────────
    logger.info("\n[STEP 7/7] Generating proposals for top ideas...")
    proposer = ProposalGenerator()
    top_ideas = sorted(
        [i for i in ideas if i.overall_score],
        key=lambda x: x.overall_score,
        reverse=True,
    )[:5]
    proposals = proposer.generate_batch(top_ideas)
    logger.info("  Generated %d proposals", len(proposals))

    # ── Print top results ───────────────────────────────────────────────
    logger.info("\n" + "=" * 70)
    logger.info("TOP 5 RESEARCH IDEAS")
    logger.info("=" * 70)
    for i, idea in enumerate(top_ideas, 1):
        logger.info("")
        logger.info("  #%d  [Rank %d]", i, i)
        logger.info("  Title:    %s", idea.title)
        logger.info("  Popul'n:  %s", idea.population)
        logger.info("  Exposure: %s", idea.exposure)
        logger.info("  Outcome:  %s", idea.outcome or "N/A")
        logger.info("  Feasibility: %.2f  |  Innovation: %.2f",
                     idea.feasibility_score or 0, idea.overall_score or 0)
        logger.info("  Gap: %s", idea.knowledge_gap[:150])

    # ── Print proposals ─────────────────────────────────────────────────
    logger.info("\n" + "=" * 70)
    logger.info("GENERATED PROPOSALS (Top 3)")
    logger.info("=" * 70)
    for prop in proposals[:3]:
        output = proposer.export_proposal(prop)
        logger.info("")
        logger.info(output[:800])

    # ── Summary ─────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info("  PDFs parsed:        %d", len(papers))
    logger.info("  Patterns mined:     %d", len(patterns))
    logger.info("  Ideas discovered:   %d", len(ideas))
    logger.info("  Proposals generated:%d", len(proposals))
    logger.info("  Graph: %d nodes, %d edges", stats["total_nodes"], stats["total_edges"])
    logger.info("=" * 70)

    return {
        "papers_parsed": len(papers),
        "patterns": len(patterns),
        "ideas": len(ideas),
        "proposals": len(proposals),
        "top_ideas": [i.model_dump() for i in top_ideas],
        "graph_stats": stats,
    }


if __name__ == "__main__":
    result = run_pipeline("pubmed")
    print("\nDone! Pipeline completed successfully.")