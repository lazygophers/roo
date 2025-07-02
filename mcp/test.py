import torch
from TTS.api import TTS
from core.config import app_name, models_path

# print(TTS().list_models())
print(models_path)

# Initialize TTS
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    model_path=models_path,
    progress_bar=True,
    gpu=torch.cuda.is_available(),
)

# List speakers
print(tts.speakers)

tts.tts(
    text="Hello world!",
    speaker="Craig Gutsy",
    language="en",
)
