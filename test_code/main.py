from stt_whisper import record_wav, transcribe_whisper
from router import get_response
from tts_pyttsx3 import speak

def main():
    print("=== Solat Voice Assistant (Selangor) ===")
    print("Tekan Enter untuk mula rakam (5 saat). Ctrl+C untuk keluar.\n")

    while True:
        input(">> Tekan Enter...")
        wav_path = record_wav(seconds=5)
        text = transcribe_whisper(wav_path, model_size="base")

        if not text:
            print("[STT] Tak dapat dengar. Cuba lagi.\n")
            speak("Maaf, saya tak dapat dengar. Boleh ulang sekali lagi?")
            continue

        print(f"[You] {text}")
        reply = get_response(text, ollama_model="llama3")
        print(f"[Bot] {reply}\n")
        speak(reply)

if __name__ == "__main__":
    main()
