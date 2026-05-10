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
