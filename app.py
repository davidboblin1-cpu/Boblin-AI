from io import BytesIO
import requests
from PIL import Image
import streamlit as st
from google import genai

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Boblin AI - Assistant Académique",
    page_icon="🎓",
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
# DESIGN & CORRECTIF DÉFILEMENT MOBILE (CSS)
# =========================================================

st.markdown(
    """
<style>
/* Permet un défilement fluide et naturel sur mobile */
html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    overflow-x: hidden;
}

.stApp {
    background: #0b0f19;
    color: #ffffff;
}

header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Conteneur principal avec une marge basse pour bien voir le dernier message */
.block-container {
    max-width: 900px;
    padding-top: 10px;
    padding-bottom: 150px;
}

.main-header {
    text-align: center;
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 12px;
    background: #1f2937;
    border: 1px solid #374151;
}

.main-header h1 {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 2px;
}

.main-header p {
    color: #9ca3af;
    font-size: 11px;
    margin: 0;
}

/* Style parfaitement lisible pour les messages */
[data-testid="stChatMessage"] {
    background: #161e2e !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    padding: 12px !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatMessage"] p, 
[data-testid="stChatMessage"] span, 
[data-testid="stChatMessage"] li {
    color: #f3f4f6 !important;
}

.stButton button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HEADER & RÉINITIALISATION
# =========================================================

col1, col2 = st.columns([5, 1], vertical_alignment="center")

with col1:
    st.markdown(
        """
        <div class="main-header">
            <h1>🎓 Boblin AI</h1>
            <p>Assistant de recherche et devoirs</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if st.button("🗑️", use_container_width=True, help="Effacer la conversation"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "✨ Nouvelle session prête. Pose ta question ou envoie une photo de ton devoir !"
        }]
        st.rerun()

# =========================================================
# INITIALISATION CHAT
# =========================================================

default_welcome = (
    "👋 **Bonjour ! Je suis Boblin AI.**\n\n"
    "Je suis là pour t'accompagner dans tes **recherches** et t'aider à résoudre tes **devoirs**.\n\n"
    "📸 *Utilise l'option ci-dessous pour joindre une photo de ton exercice ou écris ta question.*"
)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": default_welcome
    }]

# =========================================================
# IMPORTATION DE PHOTO (DEVOIRS / TEXTES)
# =========================================================

uploaded_file = st.file_uploader(
    "📸 Joindre une photo de devoir ou texte",
    type=["png", "jpg", "jpeg"]
)

uploaded_image_pil = None
if uploaded_file:
    uploaded_image_pil = Image.open(uploaded_file)
    st.image(uploaded_image_pil, caption="Photo importée", width=180)

# =========================================================
# HISTORIQUE DU CHAT (Affiche tout l'historique sans blocage)
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("input_image"):
            st.image(message["input_image"], width=150, caption="Document source")
        st.markdown(message["content"])

# =========================================================
# ENTRÉE UTILISATEUR & TRAITEMENT GEMINI
# =========================================================

prompt = st.chat_input("Écris ta question ici...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "input_image": uploaded_image_pil if uploaded_image_pil else None
    })

    with st.chat_message("user"):
        if uploaded_image_pil:
            st.image(uploaded_image_pil, width=150)
        st.markdown(prompt)

    if not client:
        st.error("⚠️ Client Gemini non initialisé. Vérifie tes clés API dans les secrets Streamlit.")
    else:
        with st.chat_message("assistant"):
            response_success = False
            attempts = 0
            max_attempts = len(API_KEYS) if API_KEYS else 1

            while not response_success and attempts < max_attempts:
                try:
                    if attempts > 0 and API_KEYS:
                        st.session_state.api_key_index += 1
                        client, _ = get_rotating_client()

                    with st.spinner("🧠 Réflexion en cours..."):
                        system_instruction = (
                            "You are Boblin AI, an expert academic tutor and research assistant. "
                            "Your goal is to help students understand their homework, solve exercises step-by-step, "
                            "and perform detailed research. Always explain clearly, provide educational breakdowns, "
                            "and respond in French. Use clean formatting and Markdown."
                        )

                        contents = []
                        if uploaded_image_pil:
                            contents.append(uploaded_image_pil)
                        
                        history_text = ""
                        for msg in st.session_state.messages[-6:]:
                            if "content" in msg and isinstance(msg["content"], str):
                                role = "Étudiant" if msg["role"] == "user" else "Boblin"
                                history_text += f"{role}: {msg['content']}\n"

                        full_prompt = f"{system_instruction}\n\nHistorique:\n{history_text}\nNouvelle consigne / Question:\n{prompt}"
                        contents.append(full_prompt)

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=contents
                        )

                        reply = response.text
                        st.markdown(reply)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": reply
                        })
                        response_success = True

                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        st.error(f"❌ Erreur API : {str(e)}")
                        break
