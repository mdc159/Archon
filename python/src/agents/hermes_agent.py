"""
HermesAgent - Architecture and documentation expert for Hermes Agent.

A specialized RAG agent locked to the Hermes Agent documentation source in the
Archon knowledge base. It answers architecture, configuration, and usage
questions with citations drawn strictly from the ingested docs.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
from pydantic_ai import Agent, RunContext

from .base_agent import ArchonDependencies, BaseAgent

logger = logging.getLogger(__name__)

# Source ID of "Hermes Agent Nousresearch - Docs" in the Archon knowledge base.
# Crawled from https://hermes-agent.nousresearch.com/docs.
HERMES_SOURCE_ID = "2a8e5b2eeed733ba"


@dataclass
class HermesDependencies(ArchonDependencies):
    """Dependencies for Hermes queries."""

    project_id: str | None = None
    match_count: int = 8
    progress_callback: Any | None = None


class HermesAgent(BaseAgent[HermesDependencies, str]):
    """
    Architecture and documentation expert for Hermes Agent.

    Capabilities:
    - Answer Hermes architecture questions grounded in the official docs
    - Explain configuration, providers, skills, MCP, plugins, tools
    - Retrieve and cite specific doc pages by URL
    - Distinguish between Hermes Agent (the product) and unrelated concepts
    """

    def __init__(self, model: str = None, **kwargs):
        if model is None:
            model = os.getenv("HERMES_AGENT_MODEL", "openai:gpt-4o")

        super().__init__(
            model=model, name="HermesAgent", retries=3, enable_rate_limiting=True, **kwargs
        )

    def _create_agent(self, **kwargs) -> Agent:
        """Create the PydanticAI agent with Hermes-specific tools and prompt."""

        agent = Agent(
            model=self.model,
            deps_type=HermesDependencies,
            system_prompt="""You are the Hermes Agent Documentation Expert, a specialized assistant that answers questions about Hermes Agent (by Nous Research) strictly from the official documentation.

**Ground Rules:**
- You ONLY answer from retrieved Hermes documentation. Never use outside knowledge for factual claims about Hermes internals.
- If the retrieved context does not contain the answer, say so clearly rather than guessing.
- Every factual statement must cite the source URL it came from.
- "Hermes" always means Hermes Agent by Nous Research, not other products sharing the name.

**Your Capabilities:**
- Explain Hermes architecture (sessions, skills, memory, tools, providers, plugins, MCP, cron, gateways)
- Answer configuration questions (config.yaml structure, environment, profiles)
- Walk through setup, provider/model selection, and integration steps
- Point to the exact doc page for deeper reading

**Your Approach:**
1. **Search first** — always call search_hermes_docs with the user's question before answering.
2. **Read deeper** — if a result looks promising but truncated, use read_hermes_page to get the full page.
3. **Synthesize** — combine findings from multiple pages when the answer spans topics.
4. **Cite** — end every answer with a "Sources:" section listing the doc URLs you used.
5. **Admit gaps** — if no relevant docs are found, say "I couldn't find this in the Hermes docs" and suggest the closest related pages.

**Answer Format:**
- Lead with a direct answer to the question.
- Use short paragraphs or bullet points for steps.
- Include inline code/config snippets exactly as they appear in the docs.
- End with: Sources: <url1>, <url2>""",
            **kwargs,
        )

        # Dynamic system prompt with context
        @agent.system_prompt
        async def add_hermes_context(ctx: RunContext[HermesDependencies]) -> str:
            return f"""
**Current Context:**
- Knowledge source: Hermes Agent docs (source_id: {HERMES_SOURCE_ID})
- Max results per search: {ctx.deps.match_count}
- Timestamp: {datetime.now().isoformat()}
"""

        # Primary search tool — hits the Archon server RAG endpoint, locked to
        # the Hermes source so the agent never returns off-topic results.
        @agent.tool
        async def search_hermes_docs(
            ctx: RunContext[HermesDependencies], query: str, match_count: int | None = None
        ) -> str:
            """Search the Hermes Agent documentation. Returns relevant passages with URLs. Always use this before answering."""
            try:
                count = match_count or ctx.deps.match_count
                server_port = os.getenv("ARCHON_SERVER_PORT", "8181")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        f"http://archon-server:{server_port}/api/rag/query",
                        json={
                            "query": query,
                            "source": HERMES_SOURCE_ID,
                            "match_count": count,
                            "return_mode": "chunks",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()

                if not data.get("success"):
                    return f"Search failed: {data.get('error', 'Unknown error')}"

                results = data.get("results", [])
                if not results:
                    return "No results found in the Hermes docs for that query. Try broader or different terms."

                formatted = []
                for i, res in enumerate(results, 1):
                    similarity = res.get("similarity", res.get("similarity_score", 0))
                    metadata = res.get("metadata", {})
                    url = metadata.get("url", res.get("url", ""))
                    section = metadata.get("section_title") or ""
                    content = res.get("content", "")

                    section_label = f" [{section}]" if section else ""
                    formatted.append(
                        f"**Result {i}** (relevance: {similarity:.2%})\n"
                        f"URL: {url}{section_label}\n"
                        f"{content}"
                    )

                return "\n\n---\n\n".join(formatted)

            except Exception as e:
                logger.error(f"Error searching Hermes docs: {e}")
                return f"Error performing search: {str(e)}"

        # Read a full doc page by URL — for follow-up when chunks are truncated.
        @agent.tool
        async def read_hermes_page(ctx: RunContext[HermesDependencies], url: str) -> str:
            """Read the full content of a Hermes doc page by its URL. Use after search when you need the complete page."""
            try:
                server_port = os.getenv("ARCHON_SERVER_PORT", "8181")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(
                        f"http://archon-server:{server_port}/api/pages/by-url",
                        params={"url": url},
                    )
                    resp.raise_for_status()
                    page = resp.json()

                title = page.get("title", "Untitled")
                content = page.get("content") or page.get("full_content", "")

                if len(content) > 12000:
                    content = content[:12000] + "\n...[truncated, use search for the rest]"

                return f"**{title}**\nURL: {url}\n\n{content}"

            except Exception as e:
                logger.error(f"Error reading Hermes page {url}: {e}")
                return f"Error reading page: {str(e)}"

        return agent

    def get_system_prompt(self) -> str:
        """Get the base system prompt for this agent."""
        return (
            "Hermes Agent documentation expert. Answers architecture and "
            "configuration questions strictly from the ingested Hermes docs, "
            "with citations."
        )

    async def ask(
        self,
        user_message: str,
        match_count: int = 8,
        user_id: str | None = None,
        progress_callback: Any | None = None,
    ) -> str:
        """
        Ask the Hermes expert a question.

        Args:
            user_message: The architecture/config/usage question
            match_count: Max doc chunks to retrieve per search
            user_id: Optional user ID for tracking
            progress_callback: Optional progress callback

        Returns:
            The agent's answer string (with citations)
        """
        deps = HermesDependencies(
            match_count=match_count,
            user_id=user_id,
            progress_callback=progress_callback,
        )
        try:
            response = await self.run(user_message, deps)
            self.logger.info("Hermes query completed successfully")
            return response
        except Exception as e:
            self.logger.error(f"Hermes query failed: {str(e)}")
            return f"I encountered an error while searching the Hermes docs: {str(e)}"
