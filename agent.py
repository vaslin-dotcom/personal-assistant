# agent.py
from dotenv import load_dotenv
from prompts import *
from remainders import *
from file_manager import *
from research import research_topic
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool, RunContext
from livekit.plugins import google, noise_cancellation
from browse import play_youtube_song
import asyncio
load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTION  # ✅ register tool at init
        )

    @function_tool()
    async def play_song(self, context: RunContext, query: str) -> str:
        """Play a song on YouTube."""
        await play_youtube_song(query)  # ensure it’s async
        return f"Playing {query} now!"

    @function_tool()
    async def remind_me(self, context: RunContext, message: str, *, after_minutes: int = None,
                        at_time: str = None) -> str:
        """Set a reminder using either relative time or absolute time."""
        return await set_reminder(context, message, after_minutes=after_minutes, at_time=at_time)

    @function_tool()
    async def research(self, context: RunContext, question: str) -> str:
        """
        Search online using Serper API and return summarized search result snippets.
        This is a wrapper around main_serper.research_topic.
        """
        # Call the research_topic function from main_serper.py
        return await research_topic(context, question)

    @function_tool()
    async def open_local_file(self, context: RunContext, filepath: str) -> str:
        """Open a local file (media will use VLC, docs/PDFs use system default)."""
        return await asyncio.to_thread(open_file, filepath)

    @function_tool()
    async def play_media(self, context: RunContext) -> str:
        """Resume playing the opened media file."""
        return await asyncio.to_thread(play)

    @function_tool()
    async def pause_media(self, context: RunContext) -> str:
        """Pause the currently playing media."""
        return await asyncio.to_thread(pause)

    @function_tool()
    async def stop_media(self, context: RunContext) -> str:
        """Stop the currently playing media."""
        return await asyncio.to_thread(stop)

    @function_tool()
    async def next_media(self, context: RunContext) -> str:
        """Play the next file in the folder playlist."""
        return await asyncio.to_thread(next_file)

    @function_tool()
    async def previous_media(self, context: RunContext) -> str:
        """Play the previous file in the folder playlist."""
        return await asyncio.to_thread(previous_file)

    @function_tool()
    async def forward_media(self, context: RunContext, seconds: int = 10) -> str:
        """Fast forward the current media (default 10 seconds)."""
        return await asyncio.to_thread(forward, seconds)

    @function_tool()
    async def backward_media(self, context: RunContext, seconds: int = 10) -> str:
        """Rewind the current media (default 10 seconds)."""
        return await asyncio.to_thread(backward, seconds)

    @function_tool()
    async def list_local_files(
            self,
            context: RunContext,
            path: str = ".",
            filter_type: str = "all",
            extension: str = None
    ) -> str:
        """List files/folders in a directory. Supports filters: 'all', 'files', 'folders', or extension (e.g., '.txt')."""
        return await asyncio.to_thread(list_files, path, filter_type, extension)



async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.8,
            instructions=INSTRUCTION + "\n\n" + REPLY,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),   # ✅ agent has the tool
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions=REPLY)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
