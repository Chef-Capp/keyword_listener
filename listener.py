import pvporcupine
import pyaudio
import struct
import datetime

from transcriber import start_recording, stop_and_transcribe, buffer_audio_data, is_recording
from dotenv import load_dotenv
load_dotenv()

print("Starting keyword listener...")

# Define keyword model paths and readable labels
keyword_files = [
    ("keywords/hey_chef.ppn", "Hey, Chef"),
    ("keywords/over_to_you_chef.ppn", "Over to you, Chef"),
    # ("keywords/cancel_chef.ppn", "Cancel, Chef")
]

keyword_paths = [f for f, _ in keyword_files]
keyword_labels = [label for _, label in keyword_files]


import os
access_key = os.environ.get("PICOVOICE_API_KEY")
if not access_key:
    raise RuntimeError("PICOVOICE_API_KEY environment variable not set.")

porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=keyword_paths
)

pa = pyaudio.PyAudio()

stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def on_hey_chef():
    print("Action: Hey, Chef - triggered")
    start_recording()

def on_over_to_you_chef():
    print("Action: Over to you, Chef - triggered")
    stop_and_transcribe()

try:
    while True:
        try:
            audio_data = stream.read(porcupine.frame_length, exception_on_overflow=False)
            buffer_audio_data(audio_data)
        except OSError as e:
            print(f"⚠️ Mic stream read error: {e}")
            continue

        frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)

        keyword_index = porcupine.process(frame)
        if keyword_index >= 0:
            timestamp = datetime.datetime.now().isoformat()
            detected_label = keyword_labels[keyword_index]
            if detected_label == "Hey, Chef" and not is_recording():
                print(f"{timestamp}")
                on_hey_chef()
            elif detected_label == "Over to you, Chef" and is_recording():
                print(f"{timestamp}")
                on_over_to_you_chef()
            # elif detected_label == "Cancel, Chef":
            #     on_cancel_chef()

finally:
    try:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"⚠️ Error closing stream: {e}")
    pa.terminate()
    porcupine.delete()