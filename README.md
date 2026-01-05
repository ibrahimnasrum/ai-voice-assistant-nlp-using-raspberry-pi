# AI Voice Assistant (Raspberry Pi) — Waktu Solat Selangor

A lightweight **AI Voice Assistant** built for **Raspberry Pi** that answers **waktu solat** (prayer times) questions for Selangor using:
- **Live microphone input** (speech-to-text)
- **Offline / local LLM** with **Ollama**
- **Domain tool** to fetch prayer times (zone-based)
- **Post-processing correction** to improve STT robustness
- Optional **Text-to-Speech (TTS)** output

Example queries:
- “Waktu asar Gombak”
- “Berapa minit lagi maghrib Gombak”
- “Waktu solat esok dekat Klang”
- “Waktu isyak dekat Sabak Bernam”

---

## Features

✅ **Live mic mode**: talk to the assistant and get instant answers  
✅ **Audio file mode**: test with `.ogg` / `.wav` recordings  
✅ **Domain-specific**: prayer times by **Selangor zones**  
✅ **Robust STT**: Faster-Whisper + custom vocabulary correction  
✅ **Fallback LLM**: if user asks non-domain questions, assistant uses local LLM (Ollama)  
✅ Optional: **TTS voice output** (speaker)

---

## System Architecture

**Voice (Mic / Audio File)**  
→ **STT (Faster-Whisper)**  
→ **Text post-processing (RapidFuzz corrections)**  
→ **Router (detect intent: prayer time / general chat)**  
→ **Prayer Tool (zone + date)** OR **Ollama LLM**  
→ **Answer (text) + optional TTS**

---

## Selangor Zone Mapping (Current)

The assistant maps locations to Selangor zones:

- **SGR01**: Gombak, Petaling, Sepang, Shah Alam, Hulu Langat, Hulu Selangor  
- **SGR02**: Kuala Selangor, Sabak Bernam  
- **SGR03**: Klang, Kuala Langat  

> You can extend this mapping in `router.py`.

---

## Requirements

### Hardware
- Raspberry Pi (recommended Pi 4 / Pi 5)
- Microphone (USB webcam mic / USB mic)
- Speaker (optional for TTS)

### Software
- Python 3.10+
- Ollama installed on Raspberry Pi (or another machine on same network)
- Internet access (only needed to fetch prayer times API)

---

## Installation (Raspberry Pi)


### 1) Clone repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>

### 2) Create venv (recommended)
python3 -m venv .venv
source .venv/bin/activate

### 3) Install dependencies
pip install -r requirements.txt

If you don’t have requirements.txt, install manually:
pip install faster-whisper sounddevice scipy numpy rapidfuzz requests python-dateutil

On Raspberry Pi, you may need PortAudio for sounddevice:
sudo apt-get update
sudo apt-get install -y portaudio19-dev


## Ollama Setup (Local LLM)

1) Install Ollama  
Follow official Ollama installation for Linux/Raspberry Pi.

2) Start Ollama service
ollama serve

3) Pull a model (example)
ollama pull llama3

You can change the model in code, e.g. llama3:latest, mistral, qwen2.5.


## Project Files (Key)

main_live_mic.py  
Live mic assistant (records audio, transcribes, answers)

main.py / mainv2.py  
Audio file mode (tests .ogg/.wav files)

stt_faster_whisper.py  
Speech-to-text using Faster-Whisper (small model)

stt_postprocess.py  
Fix common STT errors (e.g., “menit”→“minit”, “kelang”→“klang”)

router.py  
Intent routing: prayer-time domain vs general chat

prayer_tool.py  
Fetch prayer times by zone and date (today/esok/lusa, etc.)

ollama_client.py  
Calls local Ollama REST API

tts_pyttsx3.py (optional)  
Offline TTS output from speaker


## How to Run

A) Live Mic Mode (recommended)
python main_live_mic.py

You will see:
- recording prompt
- STT RAW / STT FIX
- BOT answer

B) Audio File Mode
Edit audio = "test.ogg" in test_file.py or run:
python test_file.py


## Enable Speaker Output (TTS)

Install:
pip install pyttsx3

In main_live_mic.py (or main.py) uncomment:
from tts_pyttsx3 import speak
...
speak(reply)


## Example Questions for Demo

Today
- “Waktu asar dekat Gombak”
- “Waktu maghrib dekat Klang”

Minit lagi / Dah masuk
- “Berapa minit lagi maghrib Gombak”
- “Isyak dah masuk belum Gombak”

Tomorrow / Lusa
- “Waktu solat esok dekat Gombak”
- “Waktu isyak lusa dekat Sabak Bernam”


## Troubleshooting

Mic error: Invalid sample rate / channels
Some webcam mics don’t support 16kHz directly.
This project records at the mic’s default sample rate (e.g. 48kHz) and resamples to 16kHz.

If mic still fails:
- run mic_list.py to find the correct device index
- set DEVICE_INDEX in main_live_mic.py

STT mishears locations/words
Update replacements in stt_postprocess.py:
- add place spellings / common mis-hear words
- add vocabulary words

Ollama port in use
If ollama serve shows port busy, Ollama is already running. Check:
curl http://localhost:11434/api/tags
