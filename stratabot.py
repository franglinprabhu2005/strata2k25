import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
from io import BytesIO
import time

# ✅ Page setup
st.set_page_config(page_title="🎓 STRATA 2K25 Assistant", layout="wide")

# ✅ Set background
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

# ✅ Gemini API Key
api_key = "AIzaSyBoGkf3vaZuMWmegTLM8lmVpvvoSOFYLYU"
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Load PDF brochure
@st.cache_data
def load_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        reader = PdfReader(BytesIO(response.content))
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    return ""

pdf_url = "https://drive.google.com/uc?export=download&id=1mHJGH_LOlfgLZOHCN-wTwsylrPwAboBD"
brochure_text = load_pdf_from_url(pdf_url)

# ✅ App title
st.title("🎓 STRATA 2K25 - Event Assistant Chatbot")
st.markdown("""
This chatbot helps you explore event details, rules, and participation guidelines for **STRATA 2K25**.
📘 **இந்த chatbot மூலம் STRATA 2K25 நிகழ்ச்சிகள், விதிமுறைகள் மற்றும் விவரங்களை தெரிந்து கொள்ளலாம்.**
""")

# ✅ Session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_click_time" not in st.session_state:
    st.session_state.last_click_time = 0

# ✅ Show chat history
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

# ✅ Chat input area (fixed bottom)
st.markdown("""
<div style='position: fixed; bottom: 20px; left: 0; right: 0; width: 100%; max-width: 950px; margin: auto;
            background-color: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 10px; z-index: 9999;'>
""", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("🧑 You:", placeholder="Type your question...", label_visibility="collapsed")
    with col2:
        send = st.form_submit_button("Send")

st.markdown("</div>", unsafe_allow_html=True)

# ✅ On form submit
if send and user_input.strip():
    current_time = time.time()
    if current_time - st.session_state.last_click_time < 1:
        st.warning("🚫 Please click only once bro! Double click not needed 😅")
    else:
        st.session_state.last_click_time = current_time

        with st.spinner("🕒 Your question is processing..."):
            prompt = f"""
You are a helpful event assistant for STRATA 2K25.

Refer to the following brochure content and answer the question clearly:

--- Brochure Content Start ---
{brochure_text}
--- Brochure Content End ---

Question: {user_input}
"""
            try:
                response = model.generate_content(prompt)
                answer = response.text.strip()
            except Exception as e:
                answer = f"❌ Error: {e}"

        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", answer))
