Review or scaffold the MCP setup for this portfolio project. There are two MCP servers in play:

---

## 1. Custom MCP server — `portfolio/backend/mcp_server.py`

Check if it exists. If it does, review it and suggest improvements. If it doesn't, create it.

Use FastMCP. Expose these tools (all read from curated `data/` files, no DB):

- `get_bio()` → reads `data/bio.md`, returns name, summary, personality, links, contact
- `get_skills(category: str = "")` → reads `data/skills.md`, returns skills optionally filtered by category
- `get_experience()` → reads `data/experience.md`, returns work history and education

Each tool should have a clear docstring so the LLM knows when to call it vs. the GitHub tools.

---

## 2. External GitHub MCP server — `@modelcontextprotocol/server-github`

This server is not built — it's the official GitHub MCP server consumed as an external dependency.

Document how to connect to it in `backend/agent.py` using `MultiServerMCPClient` (same pattern as `mcp_demo_client/` in the parent repo). The agent should connect to both servers simultaneously:

```python
# Conceptual — adapt to actual MultiServerMCPClient API
servers = {
    "portfolio": { "command": "python", "args": ["backend/mcp_server.py"], "transport": "stdio" },
    "github":    { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"], "transport": "stdio",
                   "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]} }
}
```

The GitHub server gives the agent these capabilities at query time:
- Search and list repos for `lukelovekin`
- Fetch README content for any specific repo
- Get recent commit activity

**Important:** the GitHub token should have `read:user` and `public_repo` scopes only. Document this in any setup instructions you write.

---

## Agent tool selection logic

After setting up both servers, explain in a comment block in `agent.py` which questions route to which server:

- "Tell me about yourself / bio / contact" → custom MCP `get_bio`
- "What are your skills / tech stack" → custom MCP `get_skills`
- "Work history / experience / education" → custom MCP `get_experience`
- "What projects have you built / show me your work" → GitHub MCP `search_repositories` + `get_readme`
- "What have you been working on lately" → GitHub MCP recent activity

The LangGraph ReAct agent decides this at runtime — just make sure the docstrings are clear enough that Claude picks correctly.
