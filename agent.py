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
import json
import datetime

load_dotenv(".env")

# --- Helpers ---
async def async_run(sync_func, *args, **kwargs):
    """Run blocking VLC/file function safely and return its result."""
    return await asyncio.to_thread(sync_func, *args, **kwargs)


def fire_and_forget(sync_func, *args, **kwargs):
    """Schedule a long-running function without awaiting."""
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: sync_func(*args, **kwargs))
    return "✅ Command sent."


# --- Assistant Class ---
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=INSTRUCTION  # register tool at init
        )

    # --- General Tools ---
    @function_tool()
    async def play_song(self, context: RunContext, query: str) -> str:
        await play_youtube_song(query)
        return f"Playing {query} now!"

    @function_tool()
    async def remind_me(self, context: RunContext, message: str, *, after_minutes: int = None,
                        at_time: str = None) -> str:
        return await set_reminder(context, message, after_minutes=after_minutes, at_time=at_time)

    @function_tool()
    async def research(self, context: RunContext, question: str) -> str:
        research_result = await research_topic(context, question)

        # Inject research block into next reply
        await context.session.generate_reply(
            instructions=f"""
            You must answer the user's question ONLY using the following trusted data:
            

            <<RESEARCH_RESULT>>
            Question: {question}
            {research_result}
            <<END_RESEARCH_RESULT>>
            """
        )

        # Also return it so LiveKit logs/tooling see it
        return research_result

    # --- Media Tools ---
    @function_tool()
    async def open_local_file(self, context: RunContext, filepath: str) -> str:
        return await async_run(open_file, filepath)

    @function_tool()
    async def play_media(self, context: RunContext) -> str:
        return await async_run(play)

    @function_tool()
    async def pause_media(self, context: RunContext) -> str:
        return await async_run(pause)

    @function_tool()
    async def stop_media(self, context: RunContext) -> str:
        return await async_run(stop)

    @function_tool()
    async def next_media(self, context: RunContext) -> str:
        return await async_run(next_file)

    @function_tool()
    async def previous_media(self, context: RunContext) -> str:
        return await async_run(previous_file)

    @function_tool()
    async def forward_media(self, context: RunContext, seconds: int = 10) -> str:
        return await async_run(forward, seconds)

    @function_tool()
    async def backward_media(self, context: RunContext, seconds: int = 10) -> str:
        return await async_run(backward, seconds)

    @function_tool()
    async def volume_up_media(self, context: RunContext, step: int = 10) -> str:
        return await async_run(volume_up, step)

    @function_tool()
    async def volume_down_media(self, context: RunContext, step: int = 10) -> str:
        return await async_run(volume_down, step)

    @function_tool()
    async def list_audio_tracks(self, context: RunContext) -> str:
        try:
            tracks = await async_run(list_audio_tracks)
            safe_tracks = [
                (tid, desc.decode("utf-8") if isinstance(desc, bytes) else desc)
                for tid, desc in tracks
            ]
            return json.dumps(safe_tracks, indent=2) if safe_tracks else "⚠️ No audio tracks found."
        except Exception as e:
            return f"⚠️ Error listing audio tracks: {str(e)}"

    @function_tool()
    async def set_audio_track(self, context: RunContext, track_id: int) -> str:
        return await async_run(change_audio_track, track_id)

    @function_tool()
    async def list_subtitle_tracks(self, context: RunContext) -> str:
        try:
            tracks = await async_run(list_subtitle_tracks)
            return json.dumps(tracks, indent=2) if tracks else "⚠️ No subtitle tracks found."
        except Exception as e:
            return f"⚠️ Error listing subtitle tracks: {str(e)}"

    @function_tool()
    async def set_subtitle_track(self, context: RunContext, track_id: int) -> str:
        return await async_run(change_subtitle_track, track_id)

    @function_tool()
    async def list_local_files(
            self,
            context: RunContext,
            path: str = ".",
            filter_type: str = "all",
            extension: str = None
    ) -> list[str]:
        return await asyncio.to_thread(list_files, path, filter_type, extension)


# --- Entrypoint ---
async def entrypoint(ctx: agents.JobContext):
    today = datetime.datetime.now().strftime("%Y-%m-%d")  # or "%B %d, %Y" for human-friendly
    instructions_with_date = INSTRUCTION + f"\n\nToday's date is: {today}\n\n" + REPLY
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.8,
            instructions=instructions_with_date,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions=REPLY)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
