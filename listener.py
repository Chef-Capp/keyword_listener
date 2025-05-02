import json
import pvporcupine  # Porcupine's keyword detector
import pyaudio      # Microphone audio input
import struct       # To unpack raw audio bytes
import datetime     # For timestamps

print("Starting keyword listener...")

# Define keyword model paths and readable labels
keyword_files = [
    ("keywords/hey_chef.ppn", "Hey, Chef"),
    ("keywords/over_to_you_chef.ppn", "Over to you, Chef"),
    #("keywords/cancel_chef.ppn", "Cancel, Chef")
]

keyword_paths = [f for f, _ in keyword_files]
keyword_labels = [label for _, label in keyword_files]

with open("secrets.json") as f:
    secrets = json.load(f)

access_key = secrets["PICOVOICE_API_KEY"]

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

def on_over_to_you_chef():
    print("Action: Over to you, Chef - triggered")

#def on_cancel_chef():
#    print("Action: Cancel, Chef triggered")

try:
    while True:
        audio_data = stream.read(porcupine.frame_length)
        frame = struct.unpack_from("h" * porcupine.frame_length, audio_data)

        keyword_index = porcupine.process(frame)
        if keyword_index >= 0:
            timestamp = datetime.datetime.now().isoformat()
            detected_label = keyword_labels[keyword_index]
            print(f"{timestamp}")
            if detected_label == "Hey, Chef":
                on_hey_chef()
            elif detected_label == "Over to you, Chef":
                on_over_to_you_chef()
            #elif detected_label == "Cancel, Chef":
            #    on_cancel_chef()

finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()