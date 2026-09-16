import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import sqlite3
from datetime import datetime
import uuid
import urllib.parse
import io
import requests

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# STYLE CSS : MODE NOIR + CORRECTION DES CHAMPS DE SAISIE
# ---------------------------------------------------------
st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stStatusWidget"] {visibility: hidden; display: none;}
        div[class*="viewerBadge"] {visibility: hidden; display: none;}

        .block-container {
            padding-top: 20px !important;
            padding-bottom: 90px !important;
        }
        
        p, h1, h2, h3, h4, h5, h6, span, label {
            color: #ffffff !important;
        }

        [data-testid="stChatInput"] textarea, [data-testid="stTextArea"] textarea {
            background-color: #1f242d !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        
        [data-testid="stChatInput"], [data-testid="stTextArea"] {
            background-color: #1f242d !important;
            border: 1px solid #30363d !important;
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PUBLICITÉS ADSTERRA
# ---------------------------------------------------------
social_bar_code = """
<script src="https://pl31368447.profitableratecpmnetwork.com/e4/11/28/e411282ec6e2782b9621884f3bb099c2.js"></script>
"""
components.html(social_bar_code, height=0)

native_banner_code = """
<script async="async" data-cfasync="false" src="https://pl31362196.profitableratecpmnetwork.com/9c55e3342fc4121417b9d5bc6db0edfc/invoke.js"></script>
<div id="container-9c55e3342fc4121417b9d5bc6db0edfc"></div>
"""

bottom_script_code = """
<script src="https://pl31366976.profitableratecpmnetwork.com/05/e6/9c/05e69c3530408f512e29bd453a2d992b.js"></script>
"""

# ---------------------------------------------------------
# BASE DE DONNÉES SQLITE POUR L'HISTORIQUE
# ---------------------------------------------------------
conn = sqlite3.connect("boblin_history.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        prompt TEXT,
        response TEXT,
        timestamp TEXT
    )
""")
conn.commit()

if "user_uuid" not in st.session_state:
    st.session_state.user_uuid = str(uuid.uuid4())

def get_current_user():
    if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
        return st.user.email
    if "custom_user_email" in st.session_state and st.session_state.custom_user_email:
        return st.session_state.custom_user_email
    return f"session_{st.session_state.user_uuid}"

def save_to_history(user_email, prompt, response):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (user_email, prompt, response, timestamp) VALUES (?, ?, ?, ?)",
                   (user_email, prompt, response, now))
    conn.commit()

def get_user_history(user_email):
    cursor.execute("SELECT prompt, response, timestamp FROM history WHERE user_email = ? ORDER BY id DESC", (user_email,))
    return cursor.fetchall()

def get_full_chat_context(user_email):
    cursor.execute("SELECT prompt, response FROM history WHERE user_email = ? ORDER BY id ASC", (user_email,))
    rows = cursor.fetchall()
    context_messages = []
    for p, r in rows:
        context_messages.append({"role": "user", "prompt": p, "response": r})
    return context_messages

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

current_user = get_current_user()

system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle textuel et multimodal interactif, similaire à ChatGPT ou Gemini. "
    "Ton nom est Boblin AI."
)

# ---------------------------------------------------------
# NAVIGATION & INTERFACE UNIFIÉE
# ---------------------------------------------------------
col_hist, col_title, col_new = st.columns([1, 2.5, 1])

with col_hist:
    if st.button("🕒", help="Historique", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

with col_title:
    st.markdown("<h4 style='text-align: center; margin: 0; color: white;'>🤖 Boblin AI</h4>", unsafe_allow_html=True)

with col_new:
    if st.button("✏️", help="Nouveau", use_container_width=True):
        st.session_state.show_history = False
        st.rerun()

st.markdown("---")
components.html(native_banner_code, height=120)
st.markdown("---")

# Option discrète pour joindre une photo à tout moment
expander_label = "➕ Ajouter une photo ou un fichier (Optionnel)"
with st.expander(expander_label, expanded=False):
    uploaded_file = st.file_uploader("Choisissez une image", type=["png", "jpg", "jpeg"])

uploaded_image_pil = None
if uploaded_file is not None:
    uploaded_image_pil = Image.open(uploaded_file)
    st.image(uploaded_image_pil, caption="Photo prête pour modification", width=150)

# ---------------------------------------------------------
# CHARGEMENT DES CLÉS API & ROTATION AUTOMATIQUE
# ---------------------------------------------------------
api_keys_list = [k.strip() for i in range(1, 16) if (k := st.secrets.get(f"GEMINI_API_KEY{i}", ""))]
if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

if not api_keys_list:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit (ex: GEMINI_API_KEY1...).")
else:
    def call_gemini_with_rotation(contents_data, is_chat=False, chat_history_list=None):
        num_keys = len(api_keys_list)
        for attempt in range(num_keys):
            current_key = api_keys_list[st.session_state.key_index]
            try:
                client = genai.Client(api_key=current_key)
                if is_chat:
                    formatted_history = []
                    for h in chat_history_list:
                        formatted_history.append({"role": "user", "parts": [{"text": h["prompt"]}]})
                        formatted_history.append({"role": "model", "parts": [{"text": h["response"]}]})
                    
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=formatted_history,
                        config={"system_instruction": system_instruction}
                    )
                else:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents_data
                    )
                return response
            except Exception as e:
                error_str = str(e)
                if any(err in error_str for err in ["429", "503", "RESOURCE_EXHAUSTED", "quota", "unavailable", "rate limit", "NOT_FOUND"]):
                    st.session_state.key_index = (st.session_state.key_index + 1) % num_keys
                    if attempt == num_keys - 1:
                        raise Exception("Toutes les clés API configurées sont actuellement saturées ou le modèle a changé. Veuillez patienter.")
                else:
                    raise e
        raise Exception("Erreur de rotation des clés.")

    # Fonction utilitaire pour afficher l'image de manière sécurisée via requests
    def render_pollinations_image(prompt_text):
        try:
            encoded_prompt = urllib.parse.quote(prompt_text)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true&seed=42"
            
            # Téléchargement des octets pour éviter l'erreur d'affichage mobile
            res = requests.get(image_url, timeout=30)
            if res.status_code == 200:
                img_obj = Image.open(io.BytesIO(res.content))
                st.image(img_obj, use_container_width=True)
                st.markdown(f"[📥 Télécharger l'image]({image_url})", unsafe_allow_html=True)
            else:
                st.error("Impossible de charger l'image générée.")
        except Exception as img_err:
            st.error(f"Erreur d'affichage de l'image : {img_err}")

    # -----------------------------------------------------
    # GESTION DE L'HISTORIQUE VS FLUX UNIFIÉ
    # -----------------------------------------------------
    if st.session_state.show_history:
        st.subheader("📜 Mon Historique")
        history_data = get_user_history(current_user)
        
        if history_data:
            for idx, item in enumerate(history_data):
                p, r, t = item
                with st.expander(f"🕒 {t} - {p[:40]}..."):
                    st.markdown(f"**Vous :** {p}")
                    if "[IMAGE_GEN]:" in r:
                        parts = r.split("[IMAGE_GEN]:")
                        st.markdown(f"**Boblin AI :** {parts[0].strip()}")
                        render_pollinations_image(parts[1].strip())
                    else:
                        st.markdown(f"**Boblin AI :** {r}")

                    if st.button(f"💬 Reprendre", key=f"continue_{idx}", use_container_width=True):
                        st.session_state.show_history = False
                        st.rerun()
        else:
            st.info("Aucun historique personnel trouvé.")
            
    else:
        chat_history_data = get_full_chat_context(current_user)
        for msg in chat_history_data:
            with st.chat_message("user"):
                st.write(msg["prompt"])
            with st.chat_message("assistant"):
                resp_text = msg["response"]
                if "[IMAGE_GEN]:" in resp_text:
                    parts = resp_text.split("[IMAGE_GEN]:")
                    st.write(parts[0].strip())
                    render_pollinations_image(parts[1].strip())
                else:
                    st.write(resp_text)

        user_prompt = st.chat_input("Discutez, analysez ou demandez à modifier/créer une image...")

        if user_prompt:
            with st.chat_message("user"):
                if uploaded_image_pil:
                    st.image(uploaded_image_pil, width=150)
                st.write(user_prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Boblin AI traite votre demande..."):
                    try:
                        lower_prompt = user_prompt.lower()
                        is_image_request = (
                            uploaded_image_pil is not None
                            or any(keyword in lower_prompt for keyword in [
                                "crée", "genere", "génère", "dessine", "image", "photo", "edit", "modify", "change", "modifier", "changer", "afro"
                            ])
                        )

                        if is_image_request:
                            if uploaded_image_pil:
                                analysis_contents = [
                                    uploaded_image_pil,
                                    (
                                        "Analyse cette image et l'instruction de l'utilisateur : "
                                        f"'{user_prompt}'. Rédige un prompt détaillé en anglais "
                                        "décrivant la version modifiée de cette image. Réponds UNIQUEMENT avec le prompt."
                                    )
                                ]
                            else:
                                analysis_contents = (
                                    "Rédige un prompt descriptif court et détaillé en anglais pour : "
                                    f"{user_prompt}. Réponds uniquement avec le prompt en anglais."
                                )

                            response_txt = call_gemini_with_rotation(analysis_contents, is_chat=False)
                            refined_prompt = response_txt.text.strip() if (response_txt and hasattr(response_txt, 'text')) else user_prompt

                            ai_response_text = f"Voici le résultat généré pour : {user_prompt}"
                            st.write(ai_response_text)
                            
                            render_pollinations_image(refined_prompt)
                            
                            save_to_history(current_user, user_prompt, f"{ai_response_text}\n[IMAGE_GEN]: {refined_prompt}")
                        else:
                            chat_history = get_full_chat_context(current_user)
                            response = call_gemini_with_rotation(None, is_chat=True, chat_history_list=chat_history)
                            ai_response_text = response.text
                            
                            st.write(ai_response_text)
                            save_to_history(current_user, user_prompt, ai_response_text)

                    except Exception as e:
                        st.error(f"Erreur : {e}")

# Affichage du script additionnel en bas de page
st.markdown("---")
components.html(bottom_script_code, height=50)
st.markdown("---")
