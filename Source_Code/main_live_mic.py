import os
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from scipy.signal import resample_poly

from stt_faster_whisper import transcribe_faster
from stt_postprocess import correct_domain_text
from router import get_response

# Optional TTS
from tts_pyttsx3 import speak

# Demo import from another folder
from demo_module import hello_world

DEVICE_INDEX = 1      # Webcam mic (WASAPI). If any issue, try 1.
SECONDS = 7
TARGET_SR = 16000

def record_to_wav(seconds: int = SECONDS) -> str:
    dev = sd.query_devices(DEVICE_INDEX)
    src_sr = int(dev["default_samplerate"])  # usually 48000 for webcam mics

    sd.default.device = (DEVICE_INDEX, None)
    print(f"[MIC] Using: {dev['name']}")
    print(f"[MIC] Recording {seconds}s at {src_sr} Hz... Speak now.")

    audio = sd.rec(int(seconds * src_sr), samplerate=src_sr, channels=1, dtype=np.float32)
    sd.wait()
    print("[MIC] Done.")

    audio = audio.squeeze()

    # Resample to 16k for STT
    audio_16k = resample_poly(audio, TARGET_SR, src_sr)

    # Float [-1,1] -> int16
    audio_16k = np.clip(audio_16k, -1.0, 1.0)
    audio_i16 = (audio_16k * 32767).astype(np.int16)

    wav_path = os.path.join(tempfile.gettempdir(), "live_input.wav")
    write(wav_path, TARGET_SR, audio_i16)
    return wav_path

def run_once():
    wav_path = record_to_wav()

    raw = transcribe_faster(wav_path)
    fixed = correct_domain_text(raw)

    print("STT RAW :", raw)
    print("STT FIX :", fixed)

    reply = get_response(fixed, ollama_model="llama3:latest")
    print("BOT:", reply)
    print("-" * 60)

    speak(reply)  # uncomment if you want voice output

def main():
    print("=== LIVE MIC: WAKTU SOLAT ASSISTANT ===")
    print("Press Enter to record. Type 'q' then Enter to quit.\n")
    
    # Test demo import
    hello_world()
    print()

    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "q":
            break
        run_once()

if __name__ == "__main__":
    main()
