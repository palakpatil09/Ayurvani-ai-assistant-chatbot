import streamlit as st
import requests
from PIL import Image
import speech_recognition as sr
import tempfile
import pyaudio
import os

# -------------------- API CONFIG -------------------- #
# Use environment variable instead of hardcoding the key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

if not GROQ_API_KEY or GROQ_API_KEY.strip() == "":
    st.error("❌ GROQ_API_KEY is missing. Please set it before running.")
    st.stop()

# -------------------- FUNCTION -------------------- #
def get_ayurvedic_remedy(query):
    """Send text query to Groq API and return Ayurvedic remedy"""
    messages = [
        {
            "role": "user",
            "content": f"{query}. Give only Ayurvedic and natural remedies, no allopathic medicines."
        }
    ]
    response = requests.post(
        GROQ_API_URL,
        json={
            "model": "llama-3.1-8b-instant",
            "messages": messages,
            "max_tokens": 800
        },
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        timeout=60
    )

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

# -------------------- STREAMLIT UI -------------------- #
st.set_page_config(page_title="🌿 Ayurvedic AI Assistant", layout="centered")
st.title("🌿 Ayurvedic AI Health Care Assistant")
st.write("Get natural Ayurvedic treatment suggestions from text, voice, or image.")

# --- Image Upload (display only) ---
uploaded_file = st.file_uploader("📸 Upload an image (optional, JPG/PNG)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

# --- Voice Input ---
st.write("🎤 Or record your concern (voice input):")

if "voice_input" not in st.session_state:
    st.session_state.voice_input = None

if st.button("Record Voice"):
    st.info("Please speak now...")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
        try:
            st.session_state.voice_input = recognizer.recognize_google(audio)
            st.success(f"You said: {st.session_state.voice_input}")
        except sr.UnknownValueError:
            st.error("Could not understand audio")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

# --- Text Input ---
query_input = st.text_input("💬 Or type your concern:")

# --- Decide which input to use ---
query = None
if st.session_state.voice_input:
    query = st.session_state.voice_input
elif query_input.strip() != "":
    query = query_input.strip()

# --- Submit Button ---
if st.button("🔍 Get Ayurvedic Remedy"):
    if not query:
        st.warning("⚠️ Please provide a concern via text or voice.")
    else:
        with st.spinner("Generating remedy... 🌿"):
            result = get_ayurvedic_remedy(query)
        st.subheader("🌸 Ayurvedic Remedy:")
        st.write(result)
