# AI Research Idea Discovery Platform
# An Intelligent Literature-to-Idea Pipeline for MIMIC-IV and eICU Research

## Vision
Transform large-scale biomedical literature into novel, feasible, and clinically meaningful research ideas for critical care databases.

## Architecture
Literature Processing -> Knowledge Base -> Pattern Mining -> Knowledge Graph -> Gap Discovery -> Feasibility Assessment -> Innovation Scoring -> Proposal Generation

## Tech Stack
- Python 3.10+
- FastAPI (API layer)
- NetworkX (Knowledge Graph)
- Pydantic (Data validation)
- SQLite (Prototype storage)
- Neo4j (Production graph store)

## Modules
- src/core: Data models, ontology, base classes
- src/literature: PDF parsing, PubMed API, knowledge extraction
- src/knowledge_graph: Graph construction, traversal, semantic retrieval
- src/pattern_mining: Research pattern decomposition, frequency analysis
- src/gap_discovery: Missing combination detection, cross-disease transfer
- src/feasibility: MIMIC-IV/eICU variable mapping, SQL complexity
- src/scoring: Multi-dimensional innovation scoring
- src/proposal: Automated research proposal generation
- src/api: REST API endpoints
- tests: Unit and integration tests
- data: Sample datasets, fixtures
- config: Configuration files
