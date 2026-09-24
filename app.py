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
# API GEMINI
# =========================================================

API_KEYS = []

try:
    for key_name in st.secrets:
        if key_name.startswith("GEMINI_API_KEY"):
            API_KEYS.append(st.secrets[key_name])
except Exception:
    API_KEYS = []


def get_client():
    if not API_KEYS:
        return None

    if "api_key_index" not in st.session_state:
        st.session_state.api_key_index = 0

    index = st.session_state.api_key_index % len(API_KEYS)
    api_key = API_KEYS[index]

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


client = get_client()


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

/* =======================================================
   GLOBAL
======================================================= */

html,
body,
.stApp {
    background:
        radial-gradient(
            circle at 50% 0%,
            rgba(110, 45, 255, 0.20),
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

    padding-top: 12px !important;
    padding-left: 20px !important;
    padding-right: 20px !important;
    padding-bottom: 150px !important;
}


/* =======================================================
   TOP BAR
======================================================= */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px;
}

</style>
""",
    unsafe_allow_html=True,
)
