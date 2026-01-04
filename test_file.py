from stt_faster_whisper import transcribe_faster
from stt_postprocess import correct_domain_text
from router import get_response

audio = "test.ogg"

raw = transcribe_faster(audio)
fixed = correct_domain_text(raw)

print("STT RAW :", raw)
print("STT FIX :", fixed)

reply = get_response(fixed, ollama_model="llama3:latest")
print("BOT:", reply)
