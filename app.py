import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered")

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

def save_to_history(user_email, prompt, response):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (user_email, prompt, response, timestamp) VALUES (?, ?, ?, ?)",
                   (user_email, prompt, response, now))
    conn.commit()

def get_user_history(user_email):
    cursor.execute("SELECT prompt, response, timestamp FROM history WHERE user_email = ? ORDER BY id DESC", (user_email,))
    return cursor.fetchall()

# ---------------------------------------------------------
# LECTURE DES CLÉS ET ROTATION (GEMINI_API_KEY1 À GEMINI_API_KEY10)
# ---------------------------------------------------------
api_keys_list = []

# Récupération de GEMINI_API_KEY1 à GEMINI_API_KEY15
for i in range(1, 15):
    key = st.secrets.get(f"GEMINI_API_KEY{i}", "")
    if key and str(key).strip():
        api_keys_list.append(str(key).strip())

# Repli si une liste sous GEMINI_API_KEYS est fournie
if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    if raw_keys:
        api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

# Saisie manuelle dans la barre latérale en absence de secret
if not api_keys_list:
    user_key_input = st.sidebar.text_input("Vos clés API (séparées par des virgules) :", type="password")
    api_keys_list = [k.strip() for k in user_key_input.split(",") if k.strip()]

if "key_index" not in st.session_state:
    st.session_state.key_index = 0

def get_current_api_key():
    if not api_keys_list:
        return None
    return api_keys_list[st.session_state.key_index % len(api_keys_list)]

def rotate_to_next_key():
    if api_keys_list:
        st.session_state.key_index = (st.session_state.key_index + 1) % len(api_keys_list)

def execute_with_key_rotation(func, *args, **kwargs):
    attempts = 0
    max_attempts = max(len(api_keys_list), 1)
    
    while attempts < max_attempts:
        current_key = get_current_api_key()
        if not current_key:
            raise Exception("Aucune clé API configurée.")
            
        try:
            genai.configure(api_key=current_key)
            return func(*args, **kwargs)
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                rotate_to_next_key()
                attempts += 1
            else:
                raise e
    raise Exception("Toutes les clés API ont atteint leur quota. Veuillez réessayer plus tard.")

# ---------------------------------------------------------
# BOUTON NOUVELLE DISCUSSION (✏️)
# ---------------------------------------------------------
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def new_chat():
    st.session_state.user_input = ""

st.sidebar.button("✏️ Nouvelle discussion", on_click=new_chat, use_container_width=True)

# ---------------------------------------------------------
# DÉTECTION COMPTE UTILISATEUR
# ---------------------------------------------------------
user_email = "Invite"
user_name = "Visiteur"

try:
    if hasattr(st, "user") and st.user:
        user_email = getattr(st.user, "email", "Invite")
        user_name = getattr(st.user, "name", "Visiteur")
except Exception:
    pass

# ---------------------------------------------------------
# MESSAGE DE BIENVENUE
# ---------------------------------------------------------
st.title("🤖 Bienvenue sur Boblin AI")

if user_email != "Invite":
    st.sidebar.success(f"Connecté : **{user_name}**")
else:
    st.sidebar.info("Connectez-vous avec Google pour sauvegarder votre historique.")

st.markdown(
    f"""
    👋 **Ravi de vous accueillir, {user_name} !**
    
    Je suis **Boblin AI**, une intelligence artificielle conçue pour vous accompagner au quotidien. Que vous ayez besoin de rédiger du contenu, de créer des images haute définition ou de retoucher vos photos, je suis là pour vous aider !
    
    ✨ *Sélectionnez une option ci-dessous et commencez à explorer mes capacités.*
    """
)

# Publicité Adsterra
adsterra_code = """
<script async="async" data-cfasync="false" src="https://pl31361635.profitableratecpmnetwork.com/cd069042531af35912924a12f1e7e736/invoke.js"></script>
<div id="container-cd069042531af35912924a12f1e7e736"></div>
"""
components.html(adsterra_code, height=100)

# ---------------------------------------------------------
# INSTRUCTION SYSTÈME DE L'IA (BOBLIN AI)
# ---------------------------------------------------------
system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle avancé, semblable à des assistants comme ChatGPT ou Gemini. "
    "Ton nom officiel est Boblin AI. Si un utilisateur te demande qui tu es, réponds clairement que tu es Boblin AI, une intelligence artificielle interactive conçue pour l'aider à générer du texte, créer ou analyser des images, répondre à ses questions et résoudre des problèmes. "
    "Sois toujours amical, précis, respectueux et serviable dans tes réponses."
)

# ---------------------------------------------------------
# FONCTIONNALITÉS
# ---------------------------------------------------------
if api_keys_list:
    mode = st.radio(
        "Choisissez une fonctionnalité :", 
        ["Texte / Chat", "Générer une Image", "Modifier une Image", "Mon Historique"]
    )

    # 1. TEXTE / CHAT
    if mode == "Texte / Chat":
        user_prompt = st.text_area("Votre message pour Boblin AI :", value=st.session_state.user_input, key="chat_input", placeholder="Qui es-tu ?")
        
        if st.button("Envoyer", type="primary"):
            if user_prompt.strip():
                with st.spinner("Boblin AI réfléchit..."):
                    try:
                        def call_chat():
                            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
                            return model.generate_content(user_prompt)
                            
                        response = execute_with_key_rotation(call_chat)
                        st.subheader("Réponse de Boblin AI :")
                        st.write(response.text)
                        save_to_history(user_email, user_prompt, response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")
            else:
                st.warning("Veuillez entrer un message.")

    # 2. GÉNÉRATION IMAGE HD
    elif mode == "Générer une Image":
        st.subheader("🖼️ Création d'Image HD")
        image_prompt = st.text_area("Décrivez l'image à générer :", placeholder="Un paysage futuriste, net, 8k...")
        
        if st.button("Générer l'Image", type="primary"):
            if image_prompt.strip():
                with st.spinner("Boblin AI génère votre image..."):
                    try:
                        enhanced_prompt = f"{image_prompt}, highly detailed, sharp focus, 8k resolution, photorealistic"
                        
                        def call_image():
                            return genai.generate_images(
                                model="imagen-3.0-generate-002",
                                prompt=enhanced_prompt,
                                number_of_images=1,
                                aspect_ratio="16:9"
                            )
                            
                        result = execute_with_key_rotation(call_image)
                        for img in result.images:
                            st.image(img._pil_image, use_container_width=True)
                        save_to_history(user_email, f"[Image] {image_prompt}", "Image générée avec succès.")
                    except Exception as e:
                        st.error(f"Erreur lors de la génération : {e}")
            else:
                st.warning("Veuillez décrire l'image.")

    # 3. MODIFICATION IMAGE
    elif mode == "Modifier une Image":
        st.subheader("🎨 Retouche et Modification d'Image")
        uploaded_image = st.file_uploader("Téléchargez l'image à analyser :", type=["jpg", "jpeg", "png", "webp"])
        edit_prompt = st.text_area("Décrivez la modification ou l'analyse :", placeholder="Décris ce qui est présent...")

        if st.button("Traiter l'image", type="primary"):
            if uploaded_image and edit_prompt.strip():
                with st.spinner("Boblin AI traite votre image..."):
                    try:
                        image = Image.open(uploaded_image)
                        
                        def call_vision():
                            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
                            return model.generate_content([edit_prompt, image])
                            
                        response = execute_with_key_rotation(call_vision)
                        st.subheader("Résultat de Boblin AI :")
                        st.write(response.text)
                        save_to_history(user_email, f"[Retouche Image] {edit_prompt}", response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")
            else:
                st.warning("Veuillez importer une image et écrire une instruction.")

    # 4. HISTORIQUE
    elif mode == "Mon Historique":
        st.subheader(f"📜 Historique de {user_name}")
        history_data = get_user_history(user_email)
        
        if history_data:
            for item in history_data:
                p, r, t = item
                with st.expander(f"🕒 {t} - {p[:40]}..."):
                    st.markdown(f"**Vous :** {p}")
                    st.markdown(f"**Boblin AI :** {r}")
        else:
            st.info("Aucun historique trouvé pour votre compte.")

    st.markdown("---")
    components.html(adsterra_code, height=100)
else:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit.")
