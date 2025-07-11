import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import requests
from io import BytesIO

# ✅ Page setup
st.set_page_config(page_title="🎓 STRATA 2K25 Assistant", layout="wide")

# ✅ Set background with dark overlay
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
        .stTextInput > div > div > input {
            background-color: #ffffff;
            border: 2px solid #ff9800;
            border-radius: 8px;
            color: black;
        }
        .stButton button {
            background-color: #ff9800;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

set_background()

# ✅ Gemini API Key
api_key = "AIzaSyBoGkf3vaZuMWmegTLM8lmVpvvoSOFYLYU"
genai.configure(api_key=api_key)

# ✅ Load Gemini Flash model
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Load PDF from a Public URL
@st.cache_data
def load_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    else:
        st.error("❌ Failed to load PDF from URL.")
        return ""
pdf_url = "https://drive.google.com/uc?export=download&id=11Y6cwo1sH9AJHT3y5IOL0J6HC8ZPHift"

# ✅ Google Drive Direct Download Link (replace FILE_ID if needed)


brochure_text = load_pdf_from_url(pdf_url)

# ✅ App Title and Info
st.title("🎓 STRATA 2K25 - Event Assistant Chatbot")
st.markdown("""
This chatbot helps you explore event details, rules, and participation guidelines for **STRATA 2K25**.

📘 **இந்த chatbot மூலம் STRATA 2K25-இல் நடைபெறும் நிகழ்ச்சிகள், விதிமுறைகள் மற்றும் விவரங்களை தெரிந்து கொள்ளலாம்.**
""")

# ✅ Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ User question input
user_input = st.text_input("❓ Ask your question about STRATA 2K25:")

# ✅ Ask button
if st.button("Ask Now"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a valid question.")
    else:
        with st.spinner("📖 Reading the brochure..."):
            prompt = f"""
You are a helpful event assistant for STRATA 2K25.

Refer to the following brochure content and answer the question clearly:

--- Brochure Content Start ---
{brochure_text[:3000]}
--- Brochure Content End ---

Question: {user_input}
"""
            try:
                response = model.generate_content(prompt)
                answer = response.text.strip()
                st.session_state.chat_history.append(("🧑 You", user_input))
                st.session_state.chat_history.append(("🤖 Bot", answer))
                st.success("✅ Here's the answer:")
                st.write(answer)
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ✅ Show chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("🗨️ Chat History")
    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}**: {msg}")
