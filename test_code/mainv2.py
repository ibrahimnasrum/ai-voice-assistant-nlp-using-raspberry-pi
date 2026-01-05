from stt_faster_whisper import transcribe_faster
from stt_postprocess import correct_domain_text
from router import get_response

# optional TTS
# from tts_pyttsx3 import speak

def run_audio_file(audio_path: str):
    raw = transcribe_faster(audio_path)
    fixed = correct_domain_text(raw)

    print("STT RAW :", raw)
    print("STT FIX :", fixed)

    reply = get_response(fixed, ollama_model="llama3:latest")
    print("BOT:", reply)

    # speak(reply)  # uncomment if you want voice output


# ---- PUT THIS AT THE BOTTOM (replace your existing __main__ block) ----
import glob, os

def latest_ogg():
    files = glob.glob("*.ogg")
    if not files:
        raise FileNotFoundError("No .ogg files found in this folder.")
    return max(files, key=os.path.getmtime)

if __name__ == "__main__":
    path = latest_ogg()
    print("Using:", path)
    run_audio_file(path)
