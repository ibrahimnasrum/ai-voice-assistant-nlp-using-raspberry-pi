import re
import requests
from rapidfuzz import process, fuzz
from gtts import gTTS
from faster_whisper import WhisperModel

# -----------------------
# 1) STT (Whisper)
# -----------------------
# If accuracy weak, try "small" instead of "base"
model = WhisperModel("base", device="cpu")

PRAYER_HINT = (
    "Bahasa Melayu. Kata penting: waktu, solat, imsak, subuh, syuruk, dhuha, zohor, asar, maghrib, isyak. "
    "Nama tempat Selangor: gombak, klang, shah alam, kuala selangor."
)

def voice_to_text(audio_path: str) -> str:
    segments, info = model.transcribe(
        audio_path,
        # Better for BM domain:
        language="ms",          # or set to None for auto-detect
        task="transcribe",
        beam_size=5,
        vad_filter=True,        # helps cut silence/noise
        initial_prompt=PRAYER_HINT
    )
    return " ".join(s.text for s in segments).strip()


# -----------------------
# 2) Prayer word correction
# -----------------------
PRAYERS_BM = ["imsak", "subuh", "syuruk", "dhuha", "zohor", "asar", "maghrib", "isyak"]

def normalize_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def correct_prayer_words(text: str, threshold: int = 80) -> str:
    words = normalize_text(text).split()
    corrected = []
    for w in words:
        match = process.extractOne(w, PRAYERS_BM, scorer=fuzz.ratio)
        if match and match[1] >= threshold:
            corrected.append(match[0])
        else:
            corrected.append(w)
    return " ".join(corrected)

def detect_prayer(text: str) -> str | None:
    t = normalize_text(text)
    for p in PRAYERS_BM:
        if re.search(rf"\b{re.escape(p)}\b", t):
            return p
    return None


# -----------------------
# 3) Get prayer times (API)
# -----------------------
# Your friend uses solat.my. Keep it if it's working for you.
# If the structure changes, print(data) once and adjust.
def get_prayer_times(zone: str = "SGR01") -> dict:
    url = f"https://solat.my/api/daily/{zone}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()

    # solat.my sometimes returns list
    if isinstance(data, list):
        data = data[0]

    # data["prayerTime"][0] is a dict like:
    # {"Imsak":"05:57:00","Fajr":"06:07:00","Dhuhr":"13:20:00","Asr":"16:43:00","Maghrib":"19:18:00","Isha":"20:32:00",...}
    return data["prayerTime"][0]

# Map BM term -> API key
BM_TO_API_KEY = {
    "imsak": "Imsak",
    "subuh": "Fajr",
    "syuruk": "Syuruk",
    "dhuha": "Dhuha",
    "zohor": "Dhuhr",
    "asar": "Asr",
    "maghrib": "Maghrib",
    "isyak": "Isha",
}


# -----------------------
# 4) TTS (gTTS)
# -----------------------
def speak(text: str, out_mp3: str = "answer.mp3", lang: str = "ms") -> str:
    tts = gTTS(text=text, lang=lang)
    tts.save(out_mp3)
    return out_mp3


# -----------------------
# 5) Response generator
# -----------------------
def generate_prayer_answer(user_text: str, zone: str = "SGR01") -> str:
    prayer = detect_prayer(user_text)
    times = get_prayer_times(zone)

    # If user asked a specific prayer
    if prayer:
        api_key = BM_TO_API_KEY.get(prayer)
        tm = times.get(api_key)
        if tm:
            return f"Waktu solat {prayer} hari ini (zon {zone}) ialah {tm[:5]}."
        return f"Maaf, saya tak jumpa waktu {prayer} untuk zon {zone}."

    # If user asked generally
    if "waktu" in normalize_text(user_text) or "time" in normalize_text(user_text):
        parts = []
        for bm in PRAYERS_BM:
            api_key = BM_TO_API_KEY[bm]
            tm = times.get(api_key, "-")
            parts.append(f"{bm.capitalize()}: {tm[:5] if isinstance(tm,str) else tm}")
        return "Waktu solat hari ini:\n" + "\n".join(parts)

    return "Maaf, saya tak pasti solat yang mana. Cuba sebut: subuh, zohor, asar, maghrib atau isyak."


def run_prayer_voice_assistant(audio_path: str, zone: str = "SGR01"):
    raw_text = voice_to_text(audio_path)
    fixed_text = correct_prayer_words(raw_text)

    print("📝 Raw STT      :", raw_text)
    print("🛠️  Corrected   :", fixed_text)

    answer = generate_prayer_answer(fixed_text, zone=zone)
    print("🤖 Answer       :", answer)

    out = speak(answer, "answer.mp3", lang="ms")
    print("🔊 Saved TTS mp3:", out)

    return fixed_text, answer


if __name__ == "__main__":
    # Example:
    # Put your audio file name here
    run_prayer_voice_assistant("test.ogg", zone="SGR01")
