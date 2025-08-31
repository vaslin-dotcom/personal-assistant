# main_serper.py
from dotenv import load_dotenv
import aiohttp
import asyncio
from livekit.agents import function_tool, RunContext
import os

load_dotenv(".env")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
@function_tool()
async def research_topic(context: RunContext, question: str) -> str:
    """
    Use Serper.dev to get top search results for a question.
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
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                return f"❌ Failed to fetch search results. Status code: {response.status}"
            data = await response.json()

    # Extract top 5 snippets from organic results
    snippets = []
    for result in data.get("organic", [])[:5]:
        snippet = result.get("snippet")
        if snippet:
            snippets.append(snippet.strip())

    if not snippets:
        return f"No results found for '{question}'."

    return f"Search result snippets for '{question}':\n" + "\n".join(snippets)


# Quick standalone test
if __name__ == "__main__":
    async def test():
        questions = [
            "IPL 2025 winner",
            "Neram movie music composer",
            "Python programming language",
            "Tesla company CEO"
        ]
        for q in questions:
            answer = await research_topic(None, q)
            print(f"Question: {q}")
            print(f"Answer: {answer}\n")

    asyncio.run(test())
