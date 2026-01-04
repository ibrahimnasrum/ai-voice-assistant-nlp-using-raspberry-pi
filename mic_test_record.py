import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from scipy.signal import resample_poly

DEVICE_INDEX = 11  # your webcam WASAPI. If issues, try 1.
SECONDS = 4
TARGET_SR = 16000  # what we want for STT

dev = sd.query_devices(DEVICE_INDEX)
SRC_SR = int(dev["default_samplerate"])  # supported rate (often 48000)

sd.default.device = (DEVICE_INDEX, None)
print("Using input device:", dev["name"])
print("Recording at:", SRC_SR, "Hz")

# record at SRC_SR
audio = sd.rec(int(SECONDS * SRC_SR), samplerate=SRC_SR, channels=1, dtype=np.float32)
sd.wait()

# flatten and resample to 16k
audio = audio.squeeze()
audio_16k = resample_poly(audio, TARGET_SR, SRC_SR)

# convert float [-1,1] -> int16
audio_16k_i16 = np.clip(audio_16k, -1.0, 1.0)
audio_16k_i16 = (audio_16k_i16 * 32767).astype(np.int16)

write("mic_test.wav", TARGET_SR, audio_16k_i16)
print("Saved: mic_test.wav (16kHz)")
