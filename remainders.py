# remainders.py
import asyncio
from datetime import datetime, timedelta
from livekit.agents import function_tool, RunContext


@function_tool()
async def get_datetime(context: RunContext) -> str:
    """Get the current date and time."""
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@function_tool()
async def set_reminder(context: RunContext, message: str, *, after_minutes: int = None, at_time: str = None) -> str:
    """
    Set a reminder either after a certain number of minutes or at a specific time.

    Args:
        message: The reminder message.
        after_minutes: Number of minutes from now.
        at_time: Absolute time in HH:MM format (24-hour). If the time has already passed today, it will schedule for tomorrow.

    Returns:
        Confirmation string.
    """

    now = datetime.now()
    delay_seconds = None

    # Determine delay
    if after_minutes is not None:
        delay_seconds = after_minutes * 60
    elif at_time is not None:
        try:
            target_time = datetime.strptime(at_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            if target_time <= now:
                # Schedule for tomorrow
                target_time += timedelta(days=1)
            delay_seconds = (target_time - now).total_seconds()
        except ValueError:
            return "❌ Invalid time format. Use HH:MM (24-hour)."
    else:
        return "❌ You must specify either 'after_minutes' or 'at_time'."

    async def reminder_task():
        await asyncio.sleep(delay_seconds)
        # Placeholder for TTS/notification integration
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(f" Reminder: {message}")
        engine.runAndWait()
        #print(f"🔔 Reminder: {message}")

    asyncio.create_task(reminder_task())

    if after_minutes is not None:
        return f"Reminder set for {after_minutes} minute(s) from now."
    else:
        return f"Reminder set for {at_time}."


# Quick test (optional)
if __name__ == "__main__":
    async def test_reminders():
        print(await get_datetime(None))
        print(await set_reminder(None, "Check the oven!", after_minutes=0.1))  # ~6 seconds
        print(await set_reminder(None, "Meeting time!", at_time="09:55"))
        await asyncio.sleep(100)  # keep loop alive

    asyncio.run(test_reminders())





















