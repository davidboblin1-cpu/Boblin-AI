import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import io
import sqlite3
from datetime import datetime
import uuid
import urllib.parse

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
    cursor.execute("SELECT prompt, response FROM history WHERE user_email = ? AND prompt NOT LIKE '[%' ORDER BY id ASC", (user_email,))
    rows = cursor.fetchall()
    context_messages = []
    for p, r in rows:
        context_messages.append({"role": "user", "parts": [{"text": p}]})
        context_messages.append({"role": "model", "parts": [{"text": r}]})
    return context_messages

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

current_user = get_current_user()

system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle textuel interactif, similaire à ChatGPT ou Gemini. "
    "Ton nom est Boblin AI."
)

# ---------------------------------------------------------
# NAVIGATION & INTERFACE
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

app_mode = st.radio("Mode", ["💬 Chat Texte", "🎨 Studio Image"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

components.html(native_banner_code, height=120)
st.markdown("---")

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
    def call_gemini_with_rotation(contents_data, is_chat=False, chat_history=None):
        num_keys = len(api_keys_list)
        for attempt in range(num_keys):
            current_key = api_keys_list[st.session_state.key_index]
            try:
                client = genai.Client(api_key=current_key)
                if is_chat:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=chat_history,
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
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    st.session_state.key_index = (st.session_state.key_index + 1) % num_keys
                    if attempt == num_keys - 1:
                        raise Exception("Toutes les clés API configurées ont atteint leur quota limite.")
                else:
                    raise e
        raise Exception("Erreur de rotation des clés.")

    # -----------------------------------------------------
    # MODE 1 : STUDIO IMAGE & GÉNÉRATION DIRECTE
    # -----------------------------------------------------
    if app_mode == "🎨 Studio Image":
        st.markdown("### 🎨 Studio Image & Animation")
        st.caption("Générez une image ou transformez votre photo directement en mode animé.")

        uploaded_file = st.file_uploader("Importer une photo (optionnel) :", type=["png", "jpg", "jpeg"])
        
        if uploaded_file:
            input_image = Image.open(uploaded_file)
            st.image(input_image, caption="Photo importée", use_container_width=True)

        image_prompt = st.text_area("Décrivez l'image ou la modification souhaitée :", placeholder="Ex: Transforme ce personnage en style animé détaillé...")

        if st.button("✨ Exécuter", use_container_width=True):
            if not image_prompt.strip():
                st.warning("Veuillez entrer une description.")
            else:
                with st.spinner("Boblin AI conçoit et génère votre image..."):
                    try:
                        # Étape 1 : On demande à Gemini 3.6 de créer un prompt visuel artistique parfait en anglais
                        if uploaded_file:
                            contents = [
                                input_image, 
                                f"Analyse cette photo et rédige un prompt descriptif ultra-détaillé en anglais pour un générateur d'images afin de la transformer selon cette consigne : {image_prompt}. Réponds uniquement avec le prompt en anglais, sans texte superflu."
                            ]
                        else:
                            contents = f"Rédige un prompt descriptif ultra-détaillé en anglais pour un générateur d'images basé sur cette demande : {image_prompt}. Réponds uniquement avec le prompt en anglais, sans texte superflu."

                        response = call_gemini_with_rotation(contents, is_chat=False)
                        
                        if response and hasattr(response, 'text'):
                            refined_prompt = response.text.strip()
                            
                            # Étape 2 : Génération et affichage direct de l'image via l'URL de rendu
                            encoded_prompt = urllib.parse.quote(refined_prompt)
                            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true"
                            
                            st.success(f"Image générée avec succès ! (Clé n°{st.session_state.key_index + 1})")
                            st.image(image_url, caption="✨ Résultat généré par Boblin AI", use_container_width=True)
                        else:
                            st.warning("Impossible de générer l'image. Veuillez réessayer.")
                            
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    # -----------------------------------------------------
    # MODE 2 : CHAT TEXTE
    # -----------------------------------------------------
    else:
        if st.session_state.show_history:
            st.subheader("📜 Mon Historique")
            history_data = get_user_history(current_user)
            
            if history_data:
                for idx, item in enumerate(history_data):
                    p, r, t = item
                    with st.expander(f"🕒 {t} - {p[:40]}..."):
                        st.markdown(f"**Vous :** {p}")
                        st.markdown(f"**Boblin AI :** {r}")
                        if st.button(f"💬 Reprendre", key=f"continue_{idx}", use_container_width=True):
                            st.session_state.show_history = False
                            st.rerun()
            else:
                st.info("Aucun historique personnel trouvé.")
                
        else:
            chat_history_data = get_full_chat_context(current_user)
            for msg in chat_history_data:
                role = "user" if msg["role"] == "user" else "assistant"
                with st.chat_message(role):
                    st.write(msg["parts"][0]["text"])

            user_prompt = st.chat_input("Posez votre question à Boblin AI...")

            if user_prompt:
                with st.chat_message("user"):
                    st.write(user_prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Boblin AI réfléchit..."):
                        try:
                            chat_history = get_full_chat_context(current_user)
                            chat_history.append({"role": "user", "parts": [{"text": user_prompt}]})
                            
                            response = call_gemini_with_rotation(None, is_chat=True, chat_history=chat_history)
                            st.write(response.text)
                            save_to_history(current_user, user_prompt, response.text)
                        except Exception as e:
                            st.error(f"Erreur : {e}")

# Affichage du script additionnel en bas de page
st.markdown("---")
components.html(bottom_script_code, height=50)
st.markdown("---")
