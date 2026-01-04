from stt_faster_whisper import transcribe_faster
from stt_postprocess import correct_domain_text

raw = transcribe_faster("mic_test.wav")
fixed = correct_domain_text(raw)

print("STT RAW :", raw)
print("STT FIX :", fixed)
