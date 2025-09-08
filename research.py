# main_serper.py
from dotenv import load_dotenv
import aiohttp
import asyncio
from livekit.agents import function_tool, RunContext
from bs4 import BeautifulSoup
import os

load_dotenv(".env")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

async def fetch_article_text(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetch and extract main text content from a given URL.
    Returns ❌ message if fetch fails.
    """
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                return None   # return None to trigger fallback
            html = await response.text()
    except Exception:
        return None   # also fallback

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    article_text = " ".join(paragraphs)

    if not article_text.strip():
        return None  # fallback if empty

    return article_text[:2000] + "..." if len(article_text) > 2000 else article_text

@function_tool()
async def research_topic(context: RunContext, question: str) -> str:
    """
    Use Serper.dev to get top search results for a question,
    try to fetch full articles, fallback to snippet if fetch fails.
    """
    url = "https://google.serper.dev/search"
    payload = {
        "q": question,
        "location": "Mumbai, Maharashtra, India",
        "gl": "in"
    }
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        # Step 1: get search results
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                return f"❌ Failed to fetch search results. Status code: {response.status}"
            data = await response.json()

        # Step 2: extract top 5 links + titles
        snippets = []
        for result in data.get("organic", [])[:2]:
            title = result.get("title")
            link = result.get("link")
            snippet = result.get("snippet")
            if not link or not title:
                continue

            # Step 3: fetch full article text (fallback to snippet if fail)
            full_text = await fetch_article_text(session, link)
            if full_text is None and snippet:
                full_text = snippet

            snippets.append(f"{title}\n{full_text}\nRead more: {link}")

    if not snippets:
        return f"No results found for '{question}'."

    return f"Search result articles for '{question}':\n\n" + "\n\n---\n\n".join(snippets)

# Quick standalone test
if __name__ == "__main__":
    async def test():
        questions = [
            "who won the ipl 2025"
        ]
        for q in questions:
            answer = await research_topic(None, q)
            print(f"Question: {q}")
            print(f"Answer: {answer}\n")

    asyncio.run(test())
