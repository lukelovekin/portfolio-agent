# Personal AI Projects

## tech-team-ai (github.com/lukelovekin/tech-team-ai)

A multi-agent AI software team that runs from the terminal. Built with the Anthropic SDK on top of Claude Code's agent infrastructure — five specialist Claude agents (Developer, Reviewer, QA, Architect, Security) that operate directly on a repository: reading actual files, running tests, searching git history, and iterating until the work meets their internal criteria.

The core idea: instead of manually orchestrating agents via chat — copying output between roles, routing context, deciding when it's done — tech-team automates that layer. One command triggers a multi-step agentic loop across multiple specialist perspectives.

Key capabilities:
- `collab` chains Architect → Developer → Reviewer + QA + Security in sequence, with the reviewer catching what the developer missed and security auditing the final state
- `check` auto-scopes to unpushed commits — agents focus only on what's changed
- A global pre-commit hook runs review and security checks on every commit across every repo automatically
- Prompt caching applied to all system prompts to reduce cost on multi-turn tool-use loops
- Installable as a CLI tool (`pip install -e .`), designed to be forked and run locally

Demonstrates: multi-agent orchestration, Claude SDK tool use, agentic loop design, CLI packaging, git hook integration, prompt caching.

---

## ai-playground (github.com/lukelovekin)
25+ self-directed AI engineering projects built to put IBM course learning into practice. Covers the full breadth of agentic AI: RAG pipelines, multi-agent systems, MCP servers, vision models, voice AI, reflection patterns, tool use, and autonomous agents. Each project is a working implementation, not a tutorial follow-along.

## This portfolio chatbot
RAG-backed AI that answers questions about Luke — ChromaDB vector search over personal data files and resume, Groq streaming (Llama 3.3 70B), Gradio UI, Pydantic state models, and per-session rate limiting. Phase 2 will add a LangGraph ReAct agent with a custom FastMCP server and live GitHub repo data via the GitHub MCP server.

## SureBuild AI

Australian construction compliance SaaS. Builders and certifiers ask NCC compliance questions or upload site photos; the system retrieves cited, jurisdiction-aware results verified against the database — the AI cannot return a hallucinated clause number.

**Backend:** FastAPI, PostgreSQL, pgvector, asyncpg, Docker

**AI/ML stack:**
- Hybrid RAG — two-stage retrieval combining pgvector dense search with PostgreSQL full-text search (tsvector/GIN), merged via weighted scoring, then cross-encoder reranking over the top candidates before passing to the LLM — production retrieval architecture, not naive vector-only search
- PydanticAI agents with structured output and tool use for retrieval; two-layer hallucination prevention: citation constraints at the prompt level plus post-run database verification — every cited clause cross-checked against the knowledge base before a response is returned
- Custom NCC knowledge graph — XML ingest pipeline parsing ABCB government documents into a clause-level vector store with typed cross-references between NCC requirements and the Australian Standards they cite; automatic jurisdiction routing per state
- RAGAS evaluation pipeline — retrieval quality measured against a fixed test set (faithfulness, context precision, context recall, answer relevancy); changes to the retrieval pipeline are score-gated, not shipped on feel
- Claude Sonnet — multimodal compliance analysis from site photos, jurisdiction-aware prompting
- OpenAI embeddings for dense retrieval; hybrid index combining cosine similarity with full-text search
- Vision pipeline (in development) — YOLOv11 detection → SAM2 segmentation → Claude reasoning; LoRA fine-tuning on a labelled Australian construction image dataset, experiment tracking with MLflow and DVC
- MCP server — exposes the compliance engine as a callable tool via the Model Context Protocol; external agents can invoke SureBuild as a tool

**Frontend:** Next.js 15, TypeScript strict, Zustand, Tailwind, react-markdown

**Integrations:** Procore and Autodesk Construction Cloud webhook connectors; MCP server for agent-to-agent interop

**Key challenge:** Compliance tooling cannot hallucinate — a wrong NCC clause number has real legal and safety consequences. The architecture replaces soft prompt constraints with a structural guarantee: post-run DB verification that cannot be circumvented by the model, combined with RAGAS-gated retrieval changes that bring measurement discipline most AI engineers skip.
