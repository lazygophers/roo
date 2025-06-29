from croe import mcp
from pync import Notifier
import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 200)  # 语速


@mcp.tool()
async def notify_system(
    message: str, title: str = "lazygophers通知", sound: str = None, say: bool = True
):
    Notifier.notify(
        message=message,
        title=title,
        sound=sound,
    )

    if say:
        await notify_tts(message)


@mcp.tool()
async def notify_tts(message: str):
    engine.say(message)
    engine.runAndWait()