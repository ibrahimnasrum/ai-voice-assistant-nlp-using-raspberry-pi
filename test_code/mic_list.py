import sounddevice as sd

print("DEFAULT", sd.default.device)
print("n=== ALL DEVICES ===")
print(sd.query_devices())
