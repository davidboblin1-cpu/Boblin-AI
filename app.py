import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
from PIL import Image
import io
import sqlite3
from datetime import datetime
import uuid

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# STYLE CSS : MODE NOIR + CORRECTION AFFICHAGE CHAT + ADS
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

        /* Correction pour TOUTES les zones de saisie (Chat Input et Text Area) */
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

        /* Conteneur pour la Native Banner */
        .native-ad-container {
            margin-top: 10px;
            margin-bottom: 10px;
            text-align: center;
            min-height: 100px; /* Espace réservé pour éviter les sauts */
            width: 100%;
            overflow: hidden;
        }
        /* Conteneur pour la bannière classique */
        .banner-ad-container {
            margin-top: 30px;
            text-align: center;
            width: 100%;
            display: flex;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INTÉGRATION PUBLICITÉS ADSTERRA (3 formats)
# ---------------------------------------------------------

# 1. Social Bar (Script flottant, invisible mais actif)
social_bar_script = """
<script type="text/javascript">
	atOptions = {
		'key' : 'VOTRE_CLE_SOCIAL_BAR_UNIQUE',
		'format' : 'iframe',
		'height' : 50,
		'width' : 320,
		'params' : {}
	};
</script>
<script type="text/javascript" src="//www.profitableratecpmnetwork.com/VOTRE_CLE_SOCIAL_BAR_UNIQUE/invoke.js"></script>
"""
# Remplacez 'VOTRE_CLE_SOCIAL_BAR_UNIQUE' par votre clé réelle Adsterra pour la Social Bar
components.html(social_bar_script, height=0)


# 2. Native Banner (S'affiche sous forme de grille de liens/images)
native_banner_code = """
<script type="text/javascript">
	atOptions = {
		'key' : 'VOTRE_CLE_NATIVE_BANNER_UNIQUE',
		'format' : 'show',
		'height' : 90,
		'width' : 728,
		'params' : {}
	};
</script>
<script type="text/javascript" src="//www.profitableratecpmnetwork.com/VOTRE_CLE_NATIVE_BANNER_UNIQUE/invoke.js"></script>
"""
# Remplacez 'VOTRE_CLE_NATIVE_BANNER_UNIQUE' par votre clé réelle Adsterra pour la Native Banner

# 3. Bannière Classique 468x60 (Format standard)
classic_banner_code = """
<script type="text/javascript">
	atOptions = {
		'key' : 'VOTRE_CLE_BANNER_468_UNIQUE',
		'format' : 'iframe',
		'height' : 60,
		'width' : 468,
		'params' : {}
	};
</script>
<script type="text/javascript" src="//www.profitableratecpmnetwork.com/VOTRE_CLE_BANNER_468_UNIQUE/invoke.js"></script>
"""
# Remplacez 'VOTRE_CLE_BANNER_468_UNIQUE' par votre clé réelle Adsterra pour la bannière 468x60


# ---------------------------------------------------------
# BASE DE DONNÉES SQLITE POUR L'HISTORIQUE PERSONNEL
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

current_user = get_current_user()

system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle textuel interactif, similaire à ChatGPT ou Gemini. "
    "Ton nom est Boblin AI. Si l'utilisateur te demande qui tu es, explique clairement que tu es Boblin AI, "
    "une intelligence artificielle créée pour l'aider à répondre à ses questions et rédiger du texte."
)

# ---------------------------------------------------------
# BARRE DE NAVIGATION SUPÉRIEURE
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

# Sélecteur de mode (Chat Texte ou Studio Image)
app_mode = st.radio("Mode", ["💬 Chat Texte", "🎨 Studio Image"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

# Insertion de la Native Banner en haut
st.markdown(f'<div class="native-ad-container">{native_banner_code}</div>', unsafe_allow_html=True)
st.markdown("---")


# ---------------------------------------------------------
# CHARGEMENT DES CLÉS API
# ---------------------------------------------------------
api_keys_list = [k.strip() for i in range(1, 16) if (k := st.secrets.get(f"GEMINI_API_KEY{i}", ""))]
if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

if not api_keys_list:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit.")
else:
    client = genai.Client(api_key=api_keys_list[0])

    # -----------------------------------------------------
    # MODE 1 : STUDIO IMAGE (Génération & Modification)
    # -----------------------------------------------------
    if app_mode == "🎨 Studio Image":
        st.markdown("### 🎨 Génération & Modification d'Images")
        st.caption("Créez de nouvelles images par description textuelle.")

        image_prompt = st.text_area("Décrivez l'image que vous souhaitez générer :", placeholder="Ex: Un chat astronaute sur Mars, style cyberpunk...")

        if st.button("✨ Exécuter", use_container_width=True):
            if not image_prompt.strip():
                st.warning("Veuillez entrer une description.")
            else:
                with st.spinner("Boblin AI crée votre image..."):
                    try:
                        # Utilisation du modèle Imagen compatible avec l'API standard
                        result = client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=image_prompt,
                            config=types.GenerateImagesConfig(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="1:1",
                                person_generation="ALLOW_ADULT",
                            )
                        )
                        for generated_image in result.generated_images:
                            image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                            st.image(image, caption="Image générée par Boblin AI", use_container_width=True)
                            st.success("Image générée avec succès !")
                            
                    except Exception as e:
                        st.error(f"Erreur lors de la génération : {e}")

    # -----------------------------------------------------
    # MODE 2 : CHAT TEXTE CLASSIQUE
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
                            
                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=chat_history,
                                config={"system_instruction": system_instruction}
                            )
                            st.write(response.text)
                            save_to_history(current_user, user_prompt, response.text)
                        except Exception as e:
                            st.error(f"Erreur : {e}")

# Insertion de la bannière classique en bas
st.markdown("---")
st.markdown(f'<div class="banner-ad-container">{classic_banner_code}</div>', unsafe_allow_html=True)
st.markdown("---")
