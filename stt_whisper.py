import os
import tempfile

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write, read as wavread

import whisper

_MODEL = None

def record_wav(seconds: int = 5, sample_rate: int = 16000) -> str:
    """
    Record from default mic and save a WAV file (16kHz mono int16).
    Returns the file path.
    """
    print(f"[MIC] Recording {seconds}s... (please speak now)")
    audio = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    print("[MIC] Done.")

    path = os.path.join(tempfile.gettempdir(), "voice_input.wav")
    write(path, sample_rate, audio)
    return path

def transcribe_whisper(wav_path: str, model_size: str = "base") -> str:
    """
    Transcribe WAV without ffmpeg by loading audio with scipy and passing numpy array to Whisper.
    """
    global _MODEL
    if _MODEL is None:
        print(f"[WHISPER] Loading model: {model_size} ...")
        _MODEL = whisper.load_model(model_size)

    sr, audio = wavread(wav_path)  # int16
    if audio.ndim > 1:
        audio = audio[:, 0]

    # Ensure float32 [-1, 1]
    audio_f32 = audio.astype(np.float32) / 32768.0

    result = _MODEL.transcribe(audio_f32, fp16=False, language="ms")
    return (result.get("text") or "").strip()
