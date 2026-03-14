"""Mock LLM service — builds a RAG prompt and streams a fake completion."""

import asyncio
from collections.abc import AsyncGenerator

from app.models import CompanyNote


def build_prompt(notes: list[CompanyNote]) -> str:
    """Assemble retrieved notes into a summarization prompt."""
    company = notes[0].company_name if notes else "Unknown"
    context_block = "\n".join(f"- [{n.created_on}] {n.notes}" for n in notes)
    return (
        f"You are a business analyst. Summarize the following notes about "
        f"{company} into a concise executive briefing.\n\n"
        f"### Notes\n{context_block}\n\n"
        f"### Summary\n"
    )


async def stream_completion(prompt: str) -> AsyncGenerator[str, None]:
    """Simulate an LLM streaming response.

    In production, replace this with an actual API call (e.g. OpenAI,
    Azure OpenAI, or a local model) that yields tokens as they arrive.
    """
    # Derive a deterministic fake summary from the prompt so it's useful
    # for testing. We just echo back a canned paragraph, token-by-token.
    fake_summary = (
        "Based on the retrieved notes, here is a high-level executive summary: "
        "The company has demonstrated steady growth underpinned by strategic "
        "market expansion in key regions. Leadership changes signal a renewed "
        "focus on financial discipline and operational efficiency. Recent "
        "contract wins in cloud infrastructure reinforce the company's "
        "commitment to digital transformation. Sustainability initiatives "
        "position the company favorably for long-term stakeholder value. "
        "Areas to watch include ongoing ERP modernization efforts and "
        "customer satisfaction trends following earlier product quality issues."
    )

    # Yield word-by-word to simulate token streaming
    for word in fake_summary.split():
        yield word + " "
        await asyncio.sleep(0.03)  # simulate network / inference latency
