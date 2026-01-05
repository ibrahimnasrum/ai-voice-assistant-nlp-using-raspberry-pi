import pyttsx3

_engine = None

def speak(text: str):
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        # Optional: tweak rate/volume if you want
        # _engine.setProperty("rate", 175)
        # _engine.setProperty("volume", 1.0)

    _engine.say(text)
    _engine.runAndWait()
