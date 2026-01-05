from stt_faster_whisper import transcribe_faster
from stt_postprocess import correct_domain_text
from router import get_response

# Optional TTS (uncomment if you have it)
# from tts_pyttsx3 import speak

import glob
import os

def run_audio_file(audio_path: str):
    raw = transcribe_faster(audio_path)
    fixed = correct_domain_text(raw)

    print("STT RAW :", raw)
    print("STT FIX :", fixed)

    reply = get_response(fixed, ollama_model="llama3:latest")
    print("BOT:", reply)

    # speak(reply)  # uncomment if you want voice output


def latest_ogg():
    files = glob.glob("*.ogg")
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def run_type_mode():
    print("Type mode (exit to quit)")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        reply = get_response(q, ollama_model="llama3:latest")
        print("BOT:", reply)
        # speak(reply)


if __name__ == "__main__":
    print("1) Type mode")
    print("2) Auto latest .ogg in folder")
    choice = input("Choose (1/2): ").strip()

    if choice == "1":
        run_type_mode()
    else:
        path = latest_ogg()
        if not path:
            print("No .ogg files found in this folder. Put an .ogg here or use Type mode.")
            raise SystemExit(1)

        print("Using:", path)
        run_audio_file(path)
