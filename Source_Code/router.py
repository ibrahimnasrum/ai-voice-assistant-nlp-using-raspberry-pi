import re
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

from prayer_tool import get_prayer_time  # returns "HH:MM:SS" or None
from ollama_client import ollama_generate


# Optional fuzzy for place typo (if rapidfuzz installed)
try:
    from rapidfuzz import process, fuzz
    _HAS_FUZZ = True
except Exception:
    _HAS_FUZZ = False


# ----------------------------
# Zone mapping (Selangor)
# ----------------------------
DEFAULT_ZONE = "SGR01"

PLACE_TO_ZONE = {
    # SGR01: Gombak + area sekitar
    "gombak": "SGR01",
    "petaling": "SGR01",
    "shah alam": "SGR01",
    "sepang": "SGR01",
    "hulu langat": "SGR01",
    "hulu selangor": "SGR01",
    "rawang": "SGR01",
    "kajang": "SGR01",

    # SGR02: Kuala Selangor + Sabak Bernam
    "kuala selangor": "SGR02",
    "sabak bernam": "SGR02",
    "tanjong karang": "SGR02",
    "tg karang": "SGR02",

    # SGR03: Klang + Kuala Langat
    "klang": "SGR03",
    "kuala langat": "SGR03",
    "banting": "SGR03",
    "jenjarom": "SGR03",
}

# Some common STT near-miss for places (extra safety)
PLACE_REWRITE = {
    "gomak": "gombak",
    "gumbang": "gombak",
    "gombang": "gombak",
}



MONTHS = {
    "januari": 1, "februari": 2, "mac": 3, "april": 4, "mei": 5, "jun": 6,
    "julai": 7, "ogos": 8, "september": 9, "oktober": 10, "november": 11, "disember": 12,
}

WEEKDAYS = {
    "isnin": 0, "selasa": 1, "rabu": 2, "khamis": 3, "jumaat": 4, "sabtu": 5, "ahad": 6,
}

def _next_weekday(d: date, target_wd: int) -> date:
    # next occurrence (including today+7 if same day)
    delta = (target_wd - d.weekday()) % 7
    if delta == 0:
        delta = 7
    return d + timedelta(days=delta)

def detect_target_date(text: str) -> tuple[date, str]:
    t = text.lower()
    today = date.today()

    # 1) Specific numeric date formats: 05/01/2026 or 05-01
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?\b", t)
    if m:
        dd = int(m.group(1)); mm = int(m.group(2))
        yy = int(m.group(3)) if m.group(3) else today.year
        cand = date(yy, mm, dd)
        if not m.group(3) and cand < today:
            cand = date(today.year + 1, mm, dd)
        return cand, cand.strftime("%d-%m-%Y")

    # 2) Specific Malay date: "5 januari" / "5 januari 2026"
    m = re.search(r"\b(\d{1,2})\s+(januari|februari|mac|april|mei|jun|julai|ogos|september|oktober|november|disember)(?:\s+(\d{4}))?\b", t)
    if m:
        dd = int(m.group(1))
        mm = MONTHS[m.group(2)]
        yy = int(m.group(3)) if m.group(3) else today.year
        cand = date(yy, mm, dd)
        if not m.group(3) and cand < today:
            cand = date(today.year + 1, mm, dd)
        return cand, cand.strftime("%d-%b-%Y")

    # 3) Weekday: "jumaat" / "jumaat depan"
    for name, wd in WEEKDAYS.items():
        if re.search(rf"\b{name}\b", t):
            cand = _next_weekday(today, wd)
            # if "minggu depan" also mentioned, push 7 more days
            if "minggu depan" in t:
                cand = cand + timedelta(days=7)
            return cand, name

    # 4) Relative keywords (priority: lusa > esok > today)
    if "lusa" in t:
        return today + timedelta(days=2), "lusa"
    if "esok" in t:
        return today + timedelta(days=1), "esok"

    # 5) Week/month ahead
    if "minggu depan" in t:
        return today + timedelta(days=7), "minggu depan"
    if "bulan depan" in t:
        return today + relativedelta(months=+1), "bulan depan"

    return today, "hari ini"

# ----------------------------
# Prayer detection
# ----------------------------
PRAYER_SYNONYMS = {
    "imsak": ["imsak"],
    "subuh": ["subuh", "fajr"],
    "syuruk": ["syuruk", "sunrise"],
    "dhuha": ["dhuha", "duha"],
    "zohor": ["zohor", "zuhur", "dzuhur", "dhuhr", "johor"],  # "johor" from STT sometimes
    "asar": ["asar", "asr", "asa"],
    "maghrib": ["maghrib", "magrib", "magreb"],
    "isyak": ["isyak", "isyah", "isha"],
}

PRAYER_CANON = list(PRAYER_SYNONYMS.keys())


# ----------------------------
# Helpers
# ----------------------------
def _norm(s: str) -> str:
    s = (s or "").lower()
    s = s.replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip()

    # quick rewrite for common place typos
    for k, v in PLACE_REWRITE.items():
        s = s.replace(k, v)
    return s


def detect_zone(text: str) -> str:
    t = _norm(text)

    # direct multi-word match first
    for place, zone in PLACE_TO_ZONE.items():
        if place in t:
            return zone

    # fuzzy fallback for phrases (2-3 words) if rapidfuzz available
    if _HAS_FUZZ:
        keys = list(PLACE_TO_ZONE.keys())
        words = t.split()

        # build n-grams (2 and 3 words) to match places like "kuala selangor"
        candidates = []
        for n in (3, 2, 1):
            for i in range(len(words) - n + 1):
                candidates.append(" ".join(words[i:i+n]))

        best_place = None
        best_score = 0
        for c in candidates:
            m = process.extractOne(c, keys, scorer=fuzz.ratio)
            if m and m[1] > best_score:
                best_place, best_score = m[0], m[1]

        if best_place and best_score >= 86:
            return PLACE_TO_ZONE[best_place]

    return DEFAULT_ZONE



def detect_prayer(text: str) -> str | None:
    t = _norm(text)

    # exact / substring match for synonyms
    for canon, syns in PRAYER_SYNONYMS.items():
        for s in syns:
            if re.search(rf"\b{re.escape(s)}\b", t):
                return canon

    # fuzzy match if user says weird spelling like "magrib"
    if _HAS_FUZZ:
        words = re.findall(r"[a-z]+", t)
        # build a synonym list to match against
        all_syns = []
        syn_to_canon = {}
        for canon, syns in PRAYER_SYNONYMS.items():
            for s in syns:
                all_syns.append(s)
                syn_to_canon[s] = canon
        for w in words:
            m = process.extractOne(w, all_syns, scorer=fuzz.ratio)
            if m and m[1] >= 85:
                return syn_to_canon[m[0]]

    return None


def is_prayer_intent(text: str) -> bool:
    t = _norm(text)
    if "waktu solat" in t or "waktu" in t:
        return True
    if "minit" in t or "berapa lama" in t or "dah masuk" in t or "masuk belum" in t:
        return True
    if detect_prayer(t):
        return True
    return False


def _minutes_until(hhmmss: str) -> int:
    """Return minutes until HH:MM:SS (Malaysia time). Negative if passed."""
    tz = ZoneInfo("Asia/Kuala_Lumpur")
    now = datetime.now(tz)
    hh, mm, ss = map(int, hhmmss.split(":"))
    target = now.replace(hour=hh, minute=mm, second=ss, microsecond=0)
    return int((target - now).total_seconds() // 60)


def build_prayer_answer(user_text: str) -> str:
    t = _norm(user_text)

    zone = detect_zone(t)
    prayer = detect_prayer(t)
    target_date, day_label = detect_target_date(t)


    ask_mins = ("berapa minit" in t) or ("minit lagi" in t) or ("berapa lama" in t) \
               or ("berapa menit" in t) or ("menit lagi" in t)
    ask_entered = ("dah masuk" in t) or ("sudah masuk" in t) or ("masuk belum" in t)

    is_today = (target_date == date.today())
    day_label = "hari ini" if is_today else ("esok" if target_date == date.today() + timedelta(days=1) else "lusa")

# Heuristic: STT sometimes hears "esok" as "isyak" in phrase "waktu solat ..."
    if "waktu solat isyak" in t and "esok" not in t and "lusa" not in t:
    # treat it as "waktu solat esok"
        t = t.replace("waktu solat isyak", "waktu solat esok")


    # --- If user asked general timetable (for the chosen day) ---
    if (("waktu solat" in t) or ("waktu hari ini" in t) or ("waktu esok" in t) or ("waktu lusa" in t)) and not prayer:
        core = ["subuh", "zohor", "asar", "maghrib", "isyak"]
        parts = []
        for p in core:
            tm = get_prayer_time(p, zone=zone, target=target_date)
            if tm:
                parts.append(f"{p.capitalize()} {tm[:5]}")
        if parts:
            return f"Waktu solat {day_label} zon {zone}: " + ", ".join(parts) + "."
        return "Maaf, saya tak dapat capai data waktu solat sekarang. Cuba lagi sekejap ya."

    # --- If prayer not identified ---
    if not prayer:
        return "Nak semak waktu solat yang mana? Subuh, zohor, asar, maghrib atau isyak?"

    # --- Get time for selected day ---
    tm = get_prayer_time(prayer, zone=zone, target=target_date)
    if not tm:
        return "Maaf, saya tak dapat capai data waktu solat sekarang. Cuba lagi sekejap ya."

    hhmm = tm[:5]

    # “minit lagi” & “dah masuk” only valid for today
    if not is_today:
        return f"Waktu solat {prayer} {day_label} untuk zon {zone} ialah {hhmm}."

    mins = _minutes_until(tm)

    if ask_entered:
        if mins <= 0:
            return f"Ya, waktu {prayer} dah masuk untuk zon {zone} ({hhmm})."
        return f"Belum. Waktu {prayer} untuk zon {zone} pukul {hhmm}, lagi lebih kurang {mins} minit."

    if ask_mins:
        if mins > 0:
            return f"Waktu {prayer} untuk zon {zone} pukul {hhmm}. Lagi lebih kurang {mins} minit."
        if mins == 0:
            return f"Sekarang dah masuk waktu {prayer} untuk zon {zone} ({hhmm})."
        return f"Waktu {prayer} untuk zon {zone} pukul {hhmm}. Waktu itu dah lepas hari ini."

    return f"Waktu solat {prayer} {day_label} untuk zon {zone} ialah {hhmm}."



def get_response(user_text: str, ollama_model: str = "llama3:latest") -> str:
    t =  _norm(user_text)

    # greeting shortcut
    if "assalamualaikum" in t:
        return "Waalaikumsalam."

    # Domain route
    if is_prayer_intent(user_text):
        return build_prayer_answer(user_text)

    # Fallback to Ollama
    prompt = (
        "Anda ialah pembantu suara ringkas dalam Bahasa Melayu.\n"
        "Jawab pendek dan jelas.\n\n"
        f"Soalan: {user_text}\nJawapan:"
    )
    return ollama_generate(prompt, model=ollama_model)
