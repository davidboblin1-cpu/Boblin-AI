from io import BytesIO
import requests
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
# DESIGN BOBLIN AI
# =========================================================

st.markdown(
    """
<style>

/* ========================================================
   GLOBAL
======================================================== */

html,
body,
.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(92, 45, 190, 0.18),
            transparent 38%
        ),
        #080914 !important;

    color: #ffffff !important;
    overscroll-behavior-y: none !important;
}

.stApp {
    min-height: 100vh;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}

/* ========================================================
   CONTENEUR
======================================================== */

.block-container {
    max-width: 720px !important;

    padding-top: 22px !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    padding-bottom: 150px !important;
}

/* ========================================================
   TOP BAR
======================================================== */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 18px;
    padding: 0 4px;
}

.top-left {
    color: #b98cff;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -3px;
}

.top-actions {
    display: flex;
    align-items: center;
    gap: 25px;

    color: white;
    font-size: 25px;
}

.top-actions span {
    opacity: 0.95;
}


/* ========================================================
   HEADER BOBLIN
======================================================== */

.boblin-header {
    position: relative;

    display: flex;
    align-items: center;

    gap: 20px;

    padding: 28px 26px;

    border-radius: 32px;

    background:
        linear-gradient(
            135deg,
            rgba(47, 25, 105, 0.70),
            rgba(11, 12, 27, 0.92)
        );

    border: 1px solid rgba(133, 81, 255, 0.45);

    box-shadow:
        0 0 35px rgba(101, 48, 255, 0.12),
        inset 0 0 30px rgba(111, 55, 255, 0.05);

    overflow: hidden;
}

.boblin-header::before {
    content: "";

    position: absolute;

    width: 
