import pyaudio
import wave
import speech_recognition as sr
import tempfile
import os
import re

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

frames = []
recording = False

def start_recording():
    global frames, recording
    print("🎙️ Started recording...")
    frames = []
    recording = True

def stop_and_transcribe():
    global frames, recording
    recording = False
    print("🛑 Stopped recording. Transcribing...")

    if not frames:
        print("⚠️ No audio captured.")
        return

    # Save to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
        wf = wave.open(tmpfile.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Transcribe with Google API
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmpfile.name) as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
            # Strip trailing "over to you chef" or similar
            text = re.sub(r"(over to you che[f]?$)", "", text.strip(), flags=re.IGNORECASE)
            print(f"📝 Transcript: {text.strip()}")
        except sr.UnknownValueError:
            print("🤔 Could not understand audio.")
        except sr.RequestError as e:
            print(f"❌ API Error: {e}")

        os.unlink(tmpfile.name)  # Delete temp file

def buffer_audio_data(data):
    global recording, frames
    if recording:
        frames.append(data)

def is_recording():
    return recording