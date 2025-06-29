import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 200)  # 语速
engine.say(" 你好，欢迎使用中文TTS")

import tempfile
import appdirs
import torch
import os
from TTS.api import TTS

from config import app_name, models_path


# # print(TTS().list_models())
# print(models_path)
#
# # Initialize TTS
# tts = TTS(
#     model_name="tts_models/multilingual/multi-dataset/xtts_v2",
#     model_path=models_path,
#     progress_bar=True,
#     gpu=torch.cuda.is_available(),
# )
#
# # List speakers
# print(tts.speakers)
#
# tts.tts(
#     text="Hello world!",
#     speaker="Craig Gutsy",
#     language="en",
# )