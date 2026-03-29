import streamlit as st
import requests
from PyPDF2 import PdfReader
from PIL import Image
import speech_recognition as sr
import time
import io

# ---------------- CONFIG ----------------
OPENROUTER_KEY = "YOUR_OPENROUTER_KEY"  # Replace with your key
BING_API_KEY = "YOUR_BING_API_KEY"      # Replace with your Bing Search API Key
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

st.set_page_config(page_title="DARK AI ULTRA CLOUD", page_icon="🖤", layout="wide")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "Normal"
if "web_search" not in st.session_state:
    st.session_state.web_search = True

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.session_state.mode = st.selectbox("Mode", ["Normal", "Coder", "YouTube"])
    st.session_state.web_search = st.checkbox("Enable Web Search", value=True)
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []

# ---------------- SYSTEM PROMPT ----------------
def get_system_prompt(mode):
    if mode == "Coder":
        return "You are an expert programmer. Provide clean, working code."
    elif mode == "YouTube":
        return "Create Hook, Script, Title, Hashtags for a short, engaging video."
    else:
        return "You are DARK AI ULTRA CLOUD — elite assistant. Give clear, structured answers."

# ---------------- OPENROUTER AI ----------------
def ask_openrouter(prompt):
    if not OPENROUTER_KEY:
        return None
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": get_system_prompt(st.session_state.mode)},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=60)
        return res.json()["choices"][0]["message"]["content"]
    except:
        return None

# ---------------- WEB SEARCH ----------------
def web_search_summary(query):
    if not BING_API_KEY:
        return "⚠️ Web Search API key not set."
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3, "textDecorations": True, "textFormat": "HTML"}
    try:
        resp = requests.get(BING_ENDPOINT, headers=headers, params=params, timeout=10)
        data = resp.json()
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append(f"**{item['name']}**\n{item.get('snippet','')}\n[Source]({item['url']})")
        return "\n\n".join(results) if results else "No search results found."
    except:
        return "⚠️ Web search error"

# ---------------- HYBRID AI ----------------
def ask_ai(prompt):
    response = ask_openrouter(prompt)
    if response:
        return "🌐 OpenRouter AI:\n" + response
    if st.session_state.web_search:
        return "🔍 Web Search:\n" + web_search_summary(prompt)
    return "⚠️ No AI available. Check OpenRouter key or Web Search."

# ---------------- FILE HANDLING ----------------
def read_pdf(file):
    try:
        pdf = PdfReader(file)
        return "".join([page.extract_text() or "" for page in pdf.pages])
    except:
        return ""

def voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        return r.recognize_google(audio)
    except:
        return ""

def typewriter(text, placeholder, speed=0.02):
    output = ""
    for char in text:
        output += char
        placeholder.markdown(f"<div style='white-space: pre-wrap;'>{output}</div>", unsafe_allow_html=True)
        time.sleep(speed)

# ---------------- UI HEADER ----------------
col1, col2 = st.columns([1,5])
with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=60)
    except:
        pass
with col2:
    st.markdown("## 🖤 DARK AI ULTRA CLOUD")

st.markdown("""
<style>
body { background-color: #0f0f0f; color: white; }
h1, h2, h3 { color: #bb86fc; }
div.stButton > button { background-color: #6200ee; color: white; border-radius: 12px; }
div.stTextInput>div>input {background-color: #1a1a1a; color: white;}
a { color: #03dac6; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
col1, col2, col3 = st.columns([3,3,2])
with col1:
    pdf_file = st.file_uploader("📄 Upload PDF", type=["pdf"])
with col2:
    img_file = st.file_uploader("🖼 Upload Image", type=["png","jpg","jpeg"])
with col3:
    if st.button("🎤 Speak"):
        spoken = voice_input()
        if spoken:
            st.session_state.messages.append({"role":"user","content":spoken})

extra = ""
if pdf_file:
    extra += read_pdf(pdf_file)
if img_file:
    try:
        img_bytes = img_file.read()
        img = Image.open(io.BytesIO(img_bytes))
        st.image(img, use_container_width=True)
        extra += "\nUser uploaded an image."
    except:
        pass

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⚡ Thinking...", unsafe_allow_html=True)
        if st.session_state.web_search:
            extra += "\n\nWeb Search Results:\n" + web_search_summary(user_input)
        response = ask_ai(user_input + "\n" + extra)
        placeholder.markdown("")
        typewriter(response, placeholder)

    st.session_state.messages.append({"role":"assistant","content":response})