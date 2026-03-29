import streamlit as st
import requests
from PyPDF2 import PdfReader
from PIL import Image
from io import BytesIO
import time
import threading

# ------------------ CONFIG ------------------
SYSTEM_PROMPT = """
You are DARK AI — a smart, concise AI assistant.
Rules:
- Give structured answers, bullets when needed
- Concise but informative
- Special modes: Normal, Coder, YouTube
"""

OPENROUTER_KEY = st.secrets.get("OPENROUTER_KEY", "")

# ------------------ SESSION STATE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------ UTILITIES ------------------
def ask_openrouter(prompt):
    if not OPENROUTER_KEY:
        return "⚠️ OpenRouter API key missing. Cannot generate responses."
    try:
        res = requests.post(
            "https://api.openrouter.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=30
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error calling OpenRouter: {e}"

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def display_message(role, content):
    cls = "user" if role=="user" else "assistant"
    with st.chat_message(role):
        st.markdown(f"<div class='{cls}'>{content}</div>", unsafe_allow_html=True)

# ------------------ STREAMLIT CONFIG ------------------
st.set_page_config(page_title="DARK AI ULTRA CLOUD", page_icon="🖤", layout="wide")

st.markdown("""
<style>
body, .block-container { background: #0f0f0f; color: #f0f0f0; font-family: 'Segoe UI', sans-serif; }
#logo { display:flex; justify-content:center; align-items:center; margin-bottom:1rem; animation:pulse 2s infinite;}
#logo img { width:50px; height:50px; margin-right:10px;}
#logo h1 { font-size:2.5rem; font-weight:bold; color:#fff;}
@keyframes pulse { 0%{transform:scale(1);}50%{transform:scale(1.1);}100%{transform:scale(1);} }
.stChatMessage { border-radius:15px; padding:10px; margin-bottom:8px; max-width:80%; }
.stChatMessage.user { background:#3b3b3b; color:#fff; align-self:flex-end; }
.stChatMessage.assistant { background:#6200ee; color:#fff; align-self:flex-start; }
div.stTextInput>div>input { border-radius:25px; padding:12px 20px; background:#1a1a1a; color:#fff; border:1px solid #6200ee; width:100%; }
button { border-radius:25px; background-color:#6200ee; color:white; border:none; padding:12px 15px; cursor:pointer; font-size:1.2rem; }
button:hover { background-color:#7b39ff; }
.footer { text-align:center; font-size:12px; color:gray; margin-top:2rem; }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("""
<div id="logo">
    <img src="logo.png" alt="logo"/>
    <h1>DARK AI ULTRA CLOUD</h1>
</div>
""", unsafe_allow_html=True)

# ------------------ UPLOAD ------------------
upload_cols = st.columns([1,1,3])
with upload_cols[0]:
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
with upload_cols[1]:
    img_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg","bmp","gif"])

# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state.messages:
    display_message(msg["role"], msg["content"])

# ------------------ INPUT ------------------
with st.container():
    input_cols = st.columns([6,1])
    with input_cols[0]:
        user_input = st.chat_input("Ask anything...")
    with input_cols[1]:
        voice_clicked = st.button("🎤")

# ------------------ HANDLE INPUT ------------------
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    display_message("user", user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("<div class='assistant'>⚡ Thinking...</div>", unsafe_allow_html=True)

        # PDF or Image text extraction
        extra = ""
        if pdf_file:
            extra += "\n" + extract_pdf_text(pdf_file)
        if img_file:
            img = Image.open(img_file)
            extra += f"\n[Image uploaded: {img_file.name}]"

        final = ask_openrouter(user_input + extra)
        placeholder.markdown(f"<div class='assistant'>{final}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role":"assistant","content":final})

# ------------------ FOOTER ------------------
st.markdown("""
<div class="footer">
<hr>
DARK AI ULTRA CLOUD can make mistakes. Verify important info.
</div>
""", unsafe_allow_html=True)