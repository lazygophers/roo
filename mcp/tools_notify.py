from croe import mcp
from pync import Notifier
import pyttsx3
from pydantic import Field

engine = pyttsx3.init()
engine.setProperty("rate", 200)  # 语速


@mcp.tool()
async def notify_system(
    message: str = Field(description="要发送的消息", examples=["hello world"]),
    title: str = Field(
        description="标题", examples=["lazygophers通知"], default="lazygophers通知"
    ),
    sound: str = Field(
        description="提示音",
        examples=[
            "Boop",
            "Ping",
            "Pong",
            "Funky",
            "Pluck",
        ],
        default=None,
    ),
    say: bool = Field(description="是否使用系统语音播报", default=True),
):
    """
    通过系统通知的方式通知
    """
    Notifier.notify(
        message=message,
        title=title,
        sound=sound,
    )

    if say:
        await notify_tts(message)


@mcp.tool()
async def notify_tts(
    message: str = Field(description="要播报的消息", examples=["消息内容"]),
):
    """
    通过语音播报的方式通知
    """
    engine.say(message)
    engine.runAndWait()
