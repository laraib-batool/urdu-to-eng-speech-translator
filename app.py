import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
from deep_translator import GoogleTranslator
import tempfile
import wave
import numpy as np
from queue import Queue

# Page setup
st.set_page_config(
    page_title="Urdu to English Speech Translator",
    page_icon="🎤",
    layout="centered"
)

st.title("🎤 Urdu → English Speech Translator")
st.write("🎙 Speak in **Urdu**, and I'll translate it into **English** for you!")

# Queue to pass results from background thread to main thread
result_queue = Queue()

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        audio_data = frame.to_ndarray()
        audio_data = np.int16(audio_data * 32767)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            with wave.open(tmpfile.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data.tobytes())

            recognizer = sr.Recognizer()
            with sr.AudioFile(tmpfile.name) as source:
                audio = recognizer.record(source)

            try:
                urdu_text = recognizer.recognize_google(audio, language="ur-PK")
                translated = GoogleTranslator(source='ur', target='en').translate(urdu_text)
                result_queue.put({"urdu": urdu_text, "english": translated})
            except Exception as e:
                result_queue.put({"error": str(e)})

        return frame

# WebRTC streamer
webrtc_streamer(
    key="speech-translator",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
)

# Display results from queue
if not result_queue.empty():
    result = result_queue.get()
    if "error" in result:
        st.error(f"Could not process audio: {result['error']}")
    else:
        st.success(f"**You said (Urdu):** {result['urdu']}")
        st.info(f"**English Translation:** {result['english']}")

st.caption("📱 Works on mobile & desktop browsers — no extra software needed.")
)

st.caption("📱 Works on mobile & desktop browsers — no extra software needed.")
