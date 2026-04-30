# Portfolio — AI Chatbot About Luke

A personal portfolio chatbot where visitors ask an AI about Luke's background, projects, and skills. The AI is grounded via RAG over personal data files and resume, streamed through Groq (Llama 3.3 70B), and served via a clean Gradio chat UI.

## What this project demonstrates

| Skill | Where |
|---|---|
| RAG pipeline | `backend/rag.py` — ChromaDB + Sentence-Transformers over personal data + resume |
| Groq streaming | `app.py` — streaming chat via Groq API (Llama 3.3 70B) |
| Pydantic state models | `backend/models.py` — ChatHistory, SessionState, RetrievedContext |
| Session management | `app.py` — per-visitor message limit + input length cap via `gr.State` |

## Architecture

```
Visitor question
      │
  Gradio UI  (app.py)
      │
  ChromaDB RAG  (backend/rag.py)
  Sentence-Transformers · data/ files + resume PDF
      │
  Groq API  (Llama 3.3 70B, streaming)
      │
  Streamed answer back to UI
```

## Phase 2 — planned (not built)

MCP was deferred because RAG over a small fixed knowledge base is simpler, faster, and more predictable. The one place MCP adds genuine value is live GitHub project data — fetching READMEs and repo metadata on demand instead of maintaining a static file.

When ready, Phase 2 will add:

```
LangGraph ReAct Agent
    ├── Custom FastMCP server         get_bio · get_skills · get_experience
    └── GitHub MCP server             live repos · READMEs · recent activity
        (@modelcontextprotocol/server-github)
```

**Why MCP for this specifically:** the GitHub data is live (new projects get pushed regularly) and structured (filter by language, topic, date). RAG over a stale markdown file is the wrong tool for that; MCP tool calls are the right one. Everything else (bio, skills, experience) stays as RAG over curated `data/` files.

## Project structure

```
portfolio/
├── .claude/
│   ├── CLAUDE.md
│   └── commands/
├── backend/
│   ├── ingest.py           # Load data/ + resume PDF into ChromaDB (run once)
│   ├── rag.py              # ChromaDB retrieval → RetrievedContext
│   └── models.py           # Pydantic: ChatHistory, SessionState, RetrievedContext
├── data/                   # Edit these, then re-run ingest.py
│   ├── bio.md              # Personal info, personality, background, what he's looking for
│   ├── skills.md           # AI/ML skills only (resume covers traditional engineering stack)
│   └── experience.md       # Project deep-dives per employer + personal AI projects
├── tests/
│   ├── test_models.py
│   └── test_ingest.py
├── app.py                  # Gradio UI + Groq streaming chat
├── lukelovekin.pdf         # Resume — primary source for work history
├── prof_portrait.JPG       # 552x552 square-cropped headshot
├── requirements.txt
├── .env.example
└── .gitignore
```

## Data files

Curated personal knowledge lives in `data/`. Edit these to change what the AI says about Luke. After editing, re-run `python backend/ingest.py` to rebuild the ChromaDB index.

- `bio.md` — personal bio, links, contact, personality, working style, engineering stack, what he's looking for
- `skills.md` — AI/ML skills only. Traditional engineering stack (Node.js, TypeScript, AWS etc.) is covered by the resume PDF
- `experience.md` — project deep-dives per employer (Montu most recent), personal AI projects

**Retrieval tuning:** CHUNK_SIZE=300 words, CHUNK_OVERLAP=50, TOP_K=4 chunks returned per query. Montu is explicitly marked as "most recent role" so "what has he worked on recently?" retrieves professional work, not personal projects.

## Running locally

```bash
# Install deps (from portfolio/ root)
python3.12 -m venv venv && source venv/bin/activate   # or: mkvenv (zsh alias)
pip install -r requirements.txt

# Build ChromaDB index (run once, re-run after any data/ or resume changes)
python backend/ingest.py

# Run app
python app.py             # http://localhost:7860
```

**zsh aliases** (in `~/.zshrc`):
- `va` — `source venv/bin/activate`
- `mkvenv` — creates venv with python3.12 and activates it

**Auto-ingest on startup:** `app.py` checks if `chroma_db/` exists at boot and runs `ingest()` automatically if not. This enables zero-config deployment on Hugging Face Spaces.

## Tests

```bash
venv/bin/pytest tests/ -v
```

Tests cover: `ChatHistory` format conversions (string + Gradio 6 block content), immutability of model mutations, `to_anthropic()` filtering of empty placeholders, `RetrievedContext.as_text()`, `SessionState` limit logic, and `chunk_text()` in ingest. No tests for trivial Pydantic construction or the Gradio UI itself.

Write tests for any new logic in `backend/models.py` or `backend/ingest.py`. Don't test Gradio component behaviour — that's integration territory.

## Gradio 6 — known quirks

This project uses Gradio 6. Several breaking changes from earlier versions apply:

- **`css` parameter** belongs in `launch()`, not `Blocks()` — `build_ui().launch(server_port=7860, css=CUSTOM_CSS)`
- **`gr.Chatbot` message format** — use `[{"role": "user", "content": "..."}, ...]` dict format, not tuples
- **Block content** — Gradio 6 passes message content as `[{"text": "...", "type": "text"}]` list instead of plain string. `ChatHistory.from_gradio()` handles both formats
- **`bubble_full_width` and `type` kwargs** — removed in Gradio 6, don't add them
- **Portrait** — rendered as base64-encoded `<img>` inside `gr.HTML`, not `gr.Image`. This gives full CSS control and avoids `show_download_button` errors

## Credentials and secrets

**Never commit secrets.** The `.env` file is in `.gitignore` and must never be committed.

Key rules:
- `GROQ_API_KEY` lives in `.env` only — loaded via `python-dotenv`, never hardcoded
- `HF_TOKEN` — HuggingFace token for Sentence-Transformers download rate limits. Both `ingest.py` and `rag.py` call `load_dotenv()` so the token is available when the embedding function initialises
- On deployment: set secrets via the hosting platform UI (HF Spaces → Settings → Secrets) — never a `.env` file on the server

`.gitignore` must include:
```
.env
__pycache__/
chroma_db/
*.pyc
```

## Deployment — Hugging Face Spaces

**Hosting:** Hugging Face Spaces (Gradio SDK, CPU Basic, Public visibility). Free tier, no credit card required.

**Setup:**
1. Create a new Space — SDK: Gradio, Template: Blank, Hardware: CPU Basic, Visibility: Public
2. Push the repo to the Space's git remote
3. Add secrets in Space Settings: `GROQ_API_KEY`, `HF_TOKEN`
4. On first boot, `app.py` auto-runs `ingest()` to build the ChromaDB index

**Storage:** ChromaDB is file-based and ephemeral on Spaces — it rebuilds on each cold start via the auto-ingest logic. Fast enough for this data size.

## Security

- **Session limit:** 30 messages per session (`SESSION_LIMIT`) — matches Groq's 30 RPM free tier limit
- **Input length limit:** 500 characters (`MESSAGE_MAX_CHARS`) — rejects oversized messages with a friendly error, prevents quota abuse
- Both limits are defined as constants at the top of `app.py`

## Environment

```env
GROQ_API_KEY=your_key          # console.groq.com — free tier, no card required
HF_TOKEN=your_token            # huggingface.co/settings/tokens — read access only
GITHUB_PERSONAL_ACCESS_TOKEN=  # Phase 2 only — read:user + public_repo scopes
GITHUB_USERNAME=lukelovekin
```

## LLM provider — why Groq

Groq is used instead of Anthropic or OpenAI because it has a genuinely free tier with no credit card required, making it safe to deploy a public portfolio site without unexpected bills.

| Provider | Free tier | Model quality | Speed |
|---|---|---|---|
| **Groq** ✓ | 14,400 req/day · 30 RPM | Llama 3.3 70B — very good | Extremely fast |
| Google Gemini Flash | 1,500 req/day · 15 RPM | Gemini 1.5 Flash — solid | Fast |
| DeepSeek | Free credits on signup, then ~$0.07/1M tokens | V3 — excellent | Moderate |
| Anthropic / OpenAI | No free tier | Best in class | Fast |

Model: `llama-3.3-70b-versatile`. Get a key at **console.groq.com**.

## Key decisions

- **Groq over Anthropic** — free tier, no card required, safe for public deployment
- **Gradio over React** — sufficient for the UI, no frontend build tooling needed
- **ChromaDB + Sentence-Transformers** — offline-capable, no additional API key
- **RAG over MCP for static data** — bio/skills/experience are curated and don't change at query time; MCP only justified for live GitHub data (Phase 2)
- **Base64 portrait in gr.HTML** — avoids Gradio Image component quirks, gives full CSS control
- **CHUNK_SIZE=300** — smaller chunks give better retrieval granularity than 500
- **No talking avatar in MVP** — deferred; clean professional chat UI is sufficient

## Custom commands

| Command | What it does |
|---|---|
| `/plan <feature>` | Design the implementation plan for a new feature |
| `/skills` | List AI skills demonstrated and where |
| `/mcp` | Scaffold or review the MCP server tools |
| `/agents` | Review agent architecture and suggest improvements |
| `/ralphloop <task>` | Iterative build → test → refine loop on a specific task |

Note: `/plan`, `/skills`, and `/ralphloop` are global commands in `~/.claude/commands/` — not repo-specific. `/mcp` and `/agents` are repo-specific in `.claude/commands/`.
