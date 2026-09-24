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
# DESIGN & CORRECTIF MOBILE (CSS)
# =========================================================

st.markdown(
    """
<style>
html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
    color: #f3f4f6;
}
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* Correction du conteneur principal pour le défilement sur mobile */
.block-container {
    max-width: 900px;
    padding-top: 20px;
    padding-bottom: 140px; /* Espace confortable pour le clavier mobile */
}

.main-header {
    text-align: center;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 16px;
    background: rgba(31, 41, 55, 0.4);
    border: 1px solid rgba(75, 85, 99, 0.3);
}

.main-header h1 {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 5px;
}

.main-header p {
    color: #9ca3af;
    font-size: 13px;
}

[data-testid="stChatMessage"] {
    background: rgba(31, 41, 55, 0.6) !important;
    border: 1px solid rgba(75, 85, 99, 0.3) !important;
    border-radius: 16px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
}

/* Fixe la barre de saisie en bas pour éviter qu'elle ne se superpose mal sur mobile */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 10px 15px;
    background: rgba(11, 15, 25, 0.95);
    backdrop-filter: blur(10px);
    z-index: 99999;
}

.stButton button {
    border-radius: 10px;
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
    st.image(uploaded_image_pil, caption="Photo importée", width=220)

# =========================================================
# HISTORIQUE DU CHAT
# =========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("input_image"):
            st.image(message["input_image"], width=180, caption="Document source")
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
            st.image(uploaded_image_pil, width=180)
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

                        # Utilisation du modèle actif recommandé
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
