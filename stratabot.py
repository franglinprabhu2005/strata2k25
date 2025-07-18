import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
from io import BytesIO
import time

# ✅ Page setup
st.set_page_config(page_title="🎓 STRATA 2K25 Assistant", layout="wide")

# ✅ Background
def set_background():
    st.markdown("""
        <style>
        body {
            background-image: url("https://images.unsplash.com/photo-1542751110-97427bbecf20?auto=format&fit=crop&w=1920&q=100");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }
        .stApp {
            background-color: rgba(0, 0, 0, 0.75);
            padding: 2rem;
            border-radius: 12px;
            max-width: 950px;
            margin: auto;
            box-shadow: 0 0 20px rgba(0,0,0,0.5);
            color: white;
        }
        h1, h2, h3, p {
            color: #ffecb3;
        }
        </style>
    """, unsafe_allow_html=True)

set_background()

# ✅ Gemini setup
api_key = "AIzaSyBoGkf3vaZuMWmegTLM8lmVpvvoSOFYLYU"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Load brochure from Google Drive
@st.cache_data
def load_pdf_from_url(url):
    res = requests.get(url)
    if res.status_code == 200:
        reader = PdfReader(BytesIO(res.content))
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return "❌ Failed to load PDF."

pdf_url = "https://drive.google.com/uc?export=download&id=1mHJGH_LOlfgLZOHCN-wTwsylrPwAboBD"

brochure_text = load_pdf_from_url(pdf_url)

# ✅ Session state init
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = 0
if "question" not in st.session_state:
    st.session_state.question = ""

# ✅ App title
st.title("🎓 STRATA 2K25 - Event Assistant Chatbot")
st.markdown("""
This chatbot helps you explore event details, rules, and participation guidelines for **STRATA 2K25**.

📘 **இந்த chatbot மூலம் STRATA 2K25 நிகழ்ச்சிகள், விதிமுறைகள் மற்றும் விவரங்களை தெரிந்து கொள்ளலாம்.**
""")

# ✅ Display chat history
st.markdown("---")
st.subheader("💬 Chat")
for role, msg in st.session_state.chat_history:
    align = "flex-end" if role == "user" else "flex-start"
    bg = "#dcf8c6" if role == "user" else "#e6e6e6"
    radius = "15px 15px 0px 15px" if role == "user" else "15px 15px 15px 0px"
    st.markdown(f"""
    <div style='display: flex; justify-content: {align}; margin: 5px 0;'>
        <div style='background-color: {bg}; padding: 10px 15px;
                    border-radius: {radius};
                    max-width: 80%; color: black; font-size: 16px;'>
            {msg}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ✅ Input box fixed bottom
st.markdown("""
<div style='position: fixed; bottom: 20px; left: 0; right: 0; width: 100%; max-width: 950px; margin: auto;
            background-color: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 10px; z-index: 9999;'>
""", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    st.text_input("🧑 You:", key="question", label_visibility="collapsed", placeholder="Type your question...")

with col2:
    clicked = st.button("Send")

st.markdown("</div>", unsafe_allow_html=True)

# ✅ Handle click
if clicked and st.session_state.question.strip():
    now = time.time()
    if now - st.session_state.last_click_time < 1:
        st.warning("🚫 Please click only once bro!")
    else:
        st.session_state.last_click_time = now

        # ✅ Safely pop the input
        user_q = st.session_state.pop("question")

        with st.spinner("🕒 Your question is processing..."):
            prompt = f"""
You are a helpful event assistant for STRATA 2K25.

Refer to the following brochure content and answer the question clearly:

--- Brochure Content Start ---
{brochure_text}
--- Brochure Content End ---

Question: {user_q}
"""
            try:
                result = model.generate_content(prompt)
                answer = result.text.strip()
            except Exception as e:
                answer = f"❌ Error: {e}"

        # ✅ Save chat
        st.session_state.chat_history.append(("user", user_q))
        st.session_state.chat_history.append(("bot", answer))
