import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

from faster_whisper import WhisperModel

_model = None

PRAYER_HINT = (
    "Bahasa Melayu. Frasa: waktu asar gombak. "
    "Waktu solat: imsak subuh zohor asar maghrib isyak. "
    "Nama tempat: gombak klang shah alam."
)

def transcribe_faster(audio_path: str, model_size: str = "small") -> str:
    global _model
    if _model is None:
        _model = WhisperModel(model_size, device="cpu")

    segments, info = _model.transcribe(
        audio_path,
        language="ms",
        beam_size=5,
        vad_filter=True,
        temperature=0.0,
        condition_on_previous_text=False,
        initial_prompt=PRAYER_HINT,
    )
    return " ".join([s.text for s in segments]).strip()
