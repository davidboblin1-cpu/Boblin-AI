from PIL import Image
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Boblin AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# GEMINI
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

    key = API_KEYS[st.session_state.api_key_index % len(API_KEYS)]

    try:
        return genai.Client(api_key=key)
    except Exception:
        return None


client = get_client()

# =========================================================
# CSS
# =========================================================

CSS = """
html, body, .stApp {
    background:
        radial-gradient(circle at 50% 0%, rgba(100,45,220,.20), transparent 38%),
        #080914 !important;
    color: white !important;
    overscroll-behavior-y: none !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden !important;
}

.block-container {
    max-width: 720px !important;
    padding: 15px 22px 150px 22px !important;
}

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
}

.boblin-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 25px 22px;
    border-radius: 30px;
    background: linear-gradient(135deg, rgba(52,27,112,.75), rgba(12,13,27,.95));
    border: 1px solid rgba(128,75,255,.55);
    box-shadow: 0 0 35px rgba(90,40,220,.15);
}

.boblin-logo {
    width: 78px;
    height: 78px;
    min-width: 78px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 24px;
    background: linear-gradient(145deg, #813cff, #4b20ca);
}

.boblin-logo span {
    font-size: 36px;
}

.boblin-info {
    flex: 1;
}

.boblin-title {
    font-size: 32px;
    font-weight: 800;
    line-height: 1;
}

.boblin-subtitle {
    margin-top: 8px;
    color: #a99bd3;
    font-size: 15px;
}

.online {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 15px;
    border-radius: 25px;
    border: 1px solid rgba(40,220,145,.45);
    background: rgba(15,70,50,.25);
    color: #4de5a0;
    font-size: 13px;
    font-weight: 600;
}

.online-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #42e89a;
    box-shadow: 0 0 12px #42e89a;
}

.upload-title {
    margin-top: 28px;
    margin-bottom: 12px;
    font-size: 19px;
}

[data-testid="stFileUploader"] section {
    background: linear-gradient(135deg, rgba(35,29,67,.95), rgba(20,20,35,.95)) !important;
    border: 1px solid rgba(125,80,255,.55) !important;
    border-radius: 24px !important;
    padding: 20px !important;
}

[data-testid="stFileUploader"] section * {
    color: white !important;
}

.hero {
    position: relative;
    margin-top: 30px;
    min-height: 430px;
    padding: 38px 30px;
    border-radius: 30px;
    overflow: hidden;
    background:
        radial-gradient(circle at 82% 65%, rgba(100,45,255,.35), transparent 25%),
        linear-gradient(145deg, #191431, #090a16);
    border: 1px solid rgba(124,76,255,.58);
}

.hero-title {
    position: relative;
    z-index: 3;
    font-size: 57px;
    line-height: .98;
    font-weight: 850;
    letter-spacing: -3px;
    margin-bottom: 30px;
}

.hero-title .purple {
    color: #a77bff;
}

.hero-description {
    position: relative;
    z-index: 3;
    max-width: 500px;
    font-size: 17px;
    line-height: 1.7;
    color: #aaa1c8;
}

.orbit {
    position: absolute;
    right: 45px;
    top: 185px;
    width: 125px;
    height: 125px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #9671ff, #4b25d4 50%, #170947);
    box-shadow: 0 0 45px rgba(95,40,255,.55);
}

.orbit:before {
    content: "";
    position: absolute;
    width: 185px;
    height: 58px;
    left: -30px;
    top: 33px;
    border: 2px solid rgba(190,160,255,.9);
    border-radius: 50%;
    transform: rotate(-18deg);
}

.orbit-dot {
    position: absolute;
    width: 15px;
    height: 15px;
    left: -20px;
    top: 82px;
    border-radius: 50%;
    background: #713cff;
    box-shadow: 0 0 18px #713cff;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, rgba(28,26,46,.96), rgba(15,15,27,.96)) !important;
    border: 1px solid rgba(126,88,255,.30) !important;
    border-radius: 22px !important;
    padding: 18px !important;
    margin-bottom: 14px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #f0eef8 !important;
    word-wrap: break-word !important;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    bottom: 18px !important;
    width: min(675px, calc(100% - 40px)) !important;
    z-index: 9999 !important;
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background: linear-gradient(135deg, rgba(39,36,55,.98), rgba(25,24,38,.98)) !important;
    border: 1px solid rgba(127,89,255,.48) !important;
    border-radius: 23px !important;
    box-shadow: 0 15px 45px rgba(0,0,0,.45) !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    background: transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #a8a1ba !important;
}

[data-testid="stChatInput"] button {
    background: #39344d !important;
    border-radius: 15px !important;
}

.manage-app {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 12px;
    margin-top: 25px;
    margin-bottom: 110px;
    color: #eeeeff;
    font-size: 16px;
}

.manage-arrow {
    font-size: 34px;
}

@media (max-width: 600px) {
    .block-container {
        padding-left: 18px !important;
        padding-right: 18px !important;
    }

    .boblin-header {
        padding: 20px 16px;
        gap: 12px;
        border-radius: 27px;
    }

    .boblin-logo {
        width: 65px;
        height: 65px;
        min-width: 65px;
    }

    .boblin-logo span {
        font-size: 30px;
    }

    .boblin-title {
        font-size: 25px;
    }

    .boblin-subtitle {
        font-size: 12px;
    }

    .online {
        padding: 8px 10px;
        font-size: 11px;
    }

    .hero {
        min-height: 480px;
        padding: 32px 24px;
    }

    .hero-title {
        font-size: 49px;
    }

    .hero-description {
        font-size: 15px;
    }

    .orbit {
        right: 40px;
        top: 310px;
        width: 105px;
        height: 105px;
    }

    .orbit:before {
        width: 155px;
        height: 50px;
    }

    [data-testid="stChatInput"] {
        width: calc(100% - 32px) !important;
        bottom: 12px !important;
    }
}
"""

st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

# =========================================================
# TOP
# =========================================================

st.markdown(
    """
    <div class="topbar">
        <div class="top-left">»</div>
        <div class="top-actions">
            <span>☆</span>
            <span>✎</span>
            <span>●</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# CHAT INIT
# =========================================================

default_welcome = """👋 **Salut !**

Comment puis-je t'aider aujourd'hui ?

Tu as :
- 📚 Un exercice à résoudre étape par étape ?
- 🔍 Un sujet de recherche à explorer ?
- ❓ Une notion de cours que tu souhaites comprendre ?
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": default_welcome}
    ]

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="boblin-header">
        <div class="boblin-logo">
            <span>🤖</span>
        </div>

        <div class="boblin-info">
            <div class="boblin-title">Boblin AI</div>
            <div class="boblin-subtitle">Creative Intelligence Studio</div>
        </div>

        <div class="online">
            <span class="online-dot"></span>
            ONLINE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# RESET
# =========================================================

if st.button("🗑️", use_container_width=True):
    st.session_state.messages = [
        {"role": "assistant", "content": default_welcome}
    ]
    st.rerun()

# =========================================================
# UPLOAD
# =========================================================

st.markdown(
    '<div class="upload-title">📸 Joindre une photo de devoir ou texte</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload",
    type=["png", "jpg", "jpeg"],
    label_visibility="collapsed",
)

uploaded_image = None

if uploaded_file is not None:
    uploaded_image = Image.open(uploaded_file)
    st.image(uploaded_image, width=220)

# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">
            Crée.<br>
            <span class="purple">Imagine.</span><br>
            Amplifie.
        </div>

        <div class="hero-description">
            Ton espace créatif propulsé par
            l'intelligence artificielle.
            Discute avec Boblin, génère des images
            et transforme tes idées en créations visuelles.
        </div>

        <div class="orbit">
            <div class="orbit-dot"></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HISTORY
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("input_image") is not None:
            st.image(message["input_image"], width=180)
        st.markdown(message["content"])

# =========================================================
# CHAT
# =========================================================

prompt = st.chat_input(
    "Écris une idée, une question ou demande une création..."
)

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "input_image": uploaded_image,
        }
    )

    with st.chat_message("user"):
        if uploaded_image is not None:
            st.image(uploaded_image, width=180)
        st.markdown(prompt)

    if client is None:
        st.error(
            "⚠️ Client Gemini non initialisé. "
            "Vérifie GEMINI_API_KEY dans les secrets Streamlit."
        )
    else:
        with st.chat_message("assistant"):
            try:
                history = ""

                for msg in st.session_state.messages[-6:]:
                    role = (
                        "Étudiant"
                        if msg["role"] == "user"
                        else "Boblin"
                    )
                    history += role + ": " + msg["content"] + "\n"

                instruction = (
                    "Tu es Boblin AI, un assistant académique expert. "
                    "Réponds toujours en français. "
                    "Explique clairement et étape par étape."
                )

                full_prompt = (
                    instruction
                    + "\n\nHistorique:\n"
                    + history
                    + "\nNouvelle question:\n"
                    + prompt
                )

                contents = []

                if uploaded_image is not None:
                    contents.append(uploaded_image)

                contents.append(full_prompt)

                with st.spinner("🧠 Boblin réfléchit..."):
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents,
                    )

                reply = response.text

                st.markdown(reply)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                    }
                )

            except Exception as error:
                st.error("❌ Erreur API : " + str(error))

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="manage-app">
        <span class="manage-arrow">‹</span>
        <span>Gérer l'application</span>
    </div>
    """,
    unsafe_allow_html=True,
)
