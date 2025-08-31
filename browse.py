#browser.py
import requests
import webbrowser
from urllib.parse import quote
import asyncio
async def play_youtube_song(query: str):
    """Search YouTube and auto-play the first result."""
    search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
    response = requests.get(search_url).text
    start = response.find("/watch?v=")
    if start == -1:
        return "No video found."
    end = response.find('"', start)
    video_url = "https://www.youtube.com" + response[start:end]
    webbrowser.open(video_url)
    return f"Playing {query} on YouTube."
if __name__ == "__main__":
    url = asyncio.run(play_youtube_song("minnal vala"))
    print("Playing on your device:", url)
    #webbrowser.open(url)