import requests
from datetime import date
from typing import Optional

ESOLAT_URL = "https://www.e-solat.gov.my/index.php?r=esolatApi/takwimsolat"

def fetch_period(zone: str, period: str = "today") -> list[dict]:
    """
    period: today | week | month | year
    Returns list of prayerTime entries.
    """
    r = requests.get(ESOLAT_URL, params={"period": period, "zone": zone}, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("prayerTime", [])

def fetch_duration(zone: str, datestart: str, dateend: str) -> list[dict]:
    """
    period=duration requires POST body: datestart/dateend in YYYY-MM-DD
    """
    r = requests.post(
        ESOLAT_URL,
        params={"period": "duration", "zone": zone},
        data={"datestart": datestart, "dateend": dateend},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("prayerTime", [])

def get_times_for_date(zone: str, target: date) -> Optional[dict]:
    """
    Return the prayer time dict for a specific date.
    """
    # easiest: fetch a week and match date
    items = fetch_period(zone, "week")
    target_str = target.strftime("%d-%b-%Y")  # e-Solat usually returns like "03-Jan-2026"
    for it in items:
        if it.get("date") == target_str:
            return it
    return None

BM_TO_KEY = {
    "imsak": "imsak",
    "subuh": "fajr",
    "syuruk": "syuruk",
    "dhuha": "dhuha",
    "zohor": "dhuhr",
    "asar": "asr",
    "maghrib": "maghrib",
    "isyak": "isha",
}

def get_prayer_time(prayer: str, zone: str, target: date) -> Optional[str]:
    day = get_times_for_date(zone, target)
    if not day:
        return None
    key = BM_TO_KEY.get(prayer)
    return day.get(key)
