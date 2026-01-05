import re
from rapidfuzz import process, fuzz

VOCAB = [
    "waktu", "solat", "dekat", "tempat", "di", "untuk",
    "imsak", "subuh", "syuruk", "dhuha", "zohor", "asar", "maghrib", "isyak",
    "gombak", "klang",
    "kuala", "selangor", "sabak", "bernam",
    "langat", "petaling", "sepang", "shah", "alam",
    "minit",

    # date/time intent words
    "hari", "ini", "esok", "lusa",
    "minggu", "depan", "hadapan",
    "bulan", "next",

    # weekdays (optional)
    "isnin", "selasa", "rabu", "khamis", "jumaat", "sabtu", "ahad",

    # months (Malay)
    "januari", "februari", "mac", "april", "mei", "jun",
    "julai", "ogos", "september", "oktober", "november", "disember",
]

REPLACE = {

    "suara": "solat",

    "dikak": "dekat",
    "dikay": "dekat",

    "kuali": "kuala",
    "selamon": "selangor",
    "sedanguk": "selangor",
    "sedanguk": "selangor",
    "sedanguk": "selangor",

    "menit": "minit",
    "waddu": "waktu",
    "waduh": "waktu",
    "asa": "asar",
    "johor": "zohor",

    # prayer/domain common errors
    "batu": "waktu",
    "soal": "solat",

    # places common STT errors
    "kelang": "klang",
    "gomak": "gombak",
    "gumbang": "gombak",

    "sahabat": "sabak",
    "sabat": "sabak",
    "bernang": "bernam",
    "benam": "bernam",

    "koal": "kuala",
    "kualis": "kuala",
    "langur": "langat",
}


def _norm(t: str) -> str:
    t = t.lower()
    for k, v in REPLACE.items():
        t = t.replace(k, v)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def correct_domain_text(text: str, threshold: int = 78) -> str:
    words = _norm(text).split()
    fixed = []
    for w in words:
        m = process.extractOne(w, VOCAB, scorer=fuzz.ratio)
        if m and m[1] >= threshold:
            fixed.append(m[0])
        else:
            fixed.append(w)
    return " ".join(fixed)
