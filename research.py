# main_serper.py
from dotenv import load_dotenv
import aiohttp
import asyncio
from livekit.agents import function_tool, RunContext
import os
import json


load_dotenv(".env")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
@function_tool()
async def research_topic(context: RunContext, question: str) -> str:
    """
    Use Serper.dev to get top search results for a question and fetch full content from links.
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

        # Extract top 3-5 organic results
        results = data.get("organic", [])[:2]  # limit to top 3 for performance

        full_results = []
        for result in results:
            snippet = result.get("snippet", "")
            link = result.get("link")
            page_content = ""
            if link:
                try:
                    async with session.get(link, timeout=10) as page_response:
                        if page_response.status == 200:
                            page_text = await page_response.text()
                            # Optional: simple cleanup to remove scripts/styles
                            import re
                            page_content = re.sub(r"<script.*?</script>", "", page_text, flags=re.DOTALL)
                            page_content = re.sub(r"<style.*?</style>", "", page_content, flags=re.DOTALL)
                            page_content = re.sub(r"<[^>]+>", "", page_content)  # remove remaining HTML tags
                            page_content = page_content.strip()[:3000]  # limit to first 3k chars
                        else:
                            page_content = f"⚠️ Could not fetch full content. HTTP {page_response.status}"
                except Exception as e:
                    page_content = f"⚠️ Error fetching full page: {str(e)}"

            full_results.append(f"- Snippet: {snippet}\n- Full content from link: {page_content}")

    if not full_results:
        return f"No results found for '{question}'."

    final_output = (
        f"<<RESEARCH_RESULT>>\n"
        f"Question: {question}\n"
        f"Results:\n" + "\n\n".join(full_results) +
        f"\n<<END_RESEARCH_RESULT>>"
    )

    print(final_output)
    return final_output


# Quick standalone test
if __name__ == "__main__":
    async def test():
        questions = [
            "first match of asia cup 2025",

        ]
        for q in questions:
            answer = await research_topic(None, q)
            print(f"Question: {q}")
            print(f"Answer: {answer}\n")

    asyncio.run(test())
