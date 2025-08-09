import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
from googletrans import Translator
import tempfile
import wave
import numpy as np

# Page setup
st.set_page_config(page_title="Urdu to English Speech Translator", page_icon="🎤", layout="centered")
st.title("🎤 Urdu → English Speech Translator")
st.write("🎙 Speak in **Urdu**, and I'll translate it into **English** for you! (Works on Mobile & Desktop)")

translator = Translator()

class AudioProcessor(AudioProcessorBase):
    def recv_audio(self, frame):
        audio_data = frame.to_ndarray()
        audio_data = np.int16(audio_data * 32767)  # Convert to 16-bit PCM

        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            with wave.open(tmpfile.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_data.tobytes())
            
            # Recognize and translate
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmpfile.name) as source:
                audio = recognizer.record(source)
            try:
                urdu_text = recognizer.recognize_google(audio, language="ur-PK")
                translation = translator.translate(urdu_text, src="ur", dest="en")
                st.success(f"**You said (Urdu):** {urdu_text}")
                st.info(f"**English Translation:** {translation.text}")
            except Exception as e:
                    st.error(f"Error: {e}")

        return frame

# WebRTC audio streamer (works in mobile browsers too)
webrtc_streamer(
    key="speech-translator",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False}
)

st.caption("📱 Works on mobile & desktop browsers — no extra software needed.")
