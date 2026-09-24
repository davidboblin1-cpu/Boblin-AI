from PIL import Image
import streamlit as st
from google import genai

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Boblin AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# API KEYS
# =========================================================

API_KEYS = []

try:
    for key_name in st.secrets:
        if key_name.startswith("GEMINI_API_KEY"):
            API_KEYS.append(st.secrets[key_name])
except Exception:
    API_KEYS = []


def get_rotating_client():
    if not API_KEYS:
        return None, None

    if "api_key_index" not in st.session_state:
        st.session_state.api_key_index = 0

    index = st.session_state.api_key_index % len(API_KEYS)
    key = API_KEYS[index]

    try:
        return genai.Client(api_key=key), key
    except Exception:
        return None, key


client, current_key = get_rotating_client()


# =========================================================
# DESIGN
# =========================================================

st.markdown(
    '''
<style>

/* =========================
   GLOBAL
========================= */

html,
body,
.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(100, 45, 220, 0.20),
            transparent 38%
        ),
        #080914 !important;

    color: #ffffff !important;
    overscroll-behavior-y: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu,
footer {
    visibility: hidden !important;
}

.block-container {
    max-width: 720px !important;
    padding-top: 15px !important;
    padding-left: 22px !important;
    padding-right: 22px !important;
    padding-bottom: 150px !important;
}


/* =========================
   TOP BAR
========================= */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 5px 5px 18px 5px;
}

.top-left {
    font-size: 34px;
    font-weight: 800;
    color: #b77cff;
}

.top-actions {
    display: flex;
    gap: 24px;
    font-size: 25px;
    color: white;
}


/* =========================
   BOBLIN HEADER
========================= */

.boblin-header {
    display: flex;
    align-items: center;
    gap: 18px;

    padding: 25px 22px;

    border-radius: 30px;

    background:
        linear-gradient(
            135deg,
            rgba(52, 27, 112, 0.75),
            rgba(12, 13, 27, 0.95)
        );

    border: 1px solid rgba
