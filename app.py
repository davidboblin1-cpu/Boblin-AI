import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
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

def get_full_chat_context(user_email):
    cursor.execute("SELECT prompt, response FROM history WHERE user_email = ? AND prompt NOT LIKE '[%' ORDER BY id ASC", (user_email,))
    rows = cursor.fetchall()
    context_messages = []
    for p, r in rows:
        context_messages.append({"role": "user", "parts": [{"text": p}]})
        context_messages.append({"role": "model", "parts": [{"text": r}]})
    return context_messages

# ---------------------------------------------------------
# GESTION DES COMPTES ET CONNEXION UTILISATEUR
# ---------------------------------------------------------
st.sidebar.markdown("### 👤 Compte utilisateur")

user_email = "Invite"
user_name = "Visiteur"

try:
    if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
        user_email = st.user.email
        user_name = getattr(st.user, "name", user_email.split("@")[0])
except Exception:
    pass

if user_email == "Invite":
    if "custom_user_email" not in st.session_state:
        st.session_state.custom_user_email = ""
    
    input_email = st.sidebar.text_input(
        "Connectez-vous avec votre e-mail / nom :", 
        value=st.session_state.custom_user_email,
        placeholder="exemple@email.com"
    )
    
    if input_email.strip():
        st.session_state.custom_user_email = input_email.strip()
        user_email = input_email.strip()
        user_name = input_email.strip().split("@")[0]
        st.sidebar.success(f"Connecté : **{user_name}**")
    else:
        st.sidebar.info("💡 Entrez un email pour enregistrer votre propre historique.")
else:
    st.sidebar.success(f"Connecté : **{user_name}** ({user_email})")

# ---------------------------------------------------------
# LECTURE ET ROTATION DES CLÉS API (GEMINI_API_KEY1 À 15)
# ---------------------------------------------------------
api_keys_list = []

for i in range(1, 16):
    key = st.secrets.get(f"GEMINI_API_KEY{i}", "")
    if key and str(key).strip():
        api_keys_list.append(str(key).strip())

if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    if raw_keys:
        api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

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
            client = genai.Client(api_key=current_key)
            return func(client, *args, **kwargs)
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                rotate_to_next_key()
                attempts += 1
            else:
                raise e
    raise Exception("Toutes les clés API ont atteint leur quota. Veuillez réessayer plus tard.")

# ---------------------------------------------------------
# GESTION DES MODÈLES DYNAMIQUES
# ---------------------------------------------------------
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-3.6-flash"
]

def generate_text_smart(client, contents, system_instruction):
    last_error = None
    for model_name in MODEL_CANDIDATES:
        try:
            return client.models.generate_content(
                model=model_name,
                contents=contents,
                config={"system_instruction": system_instruction}
            )
        except Exception as err:
            last_error = err
            if "404" in str(err) or "not found" in str(err).lower():
                continue
            raise err
    raise last_error

# ---------------------------------------------------------
# NAVIGATION & ETAT SESSION
# ---------------------------------------------------------
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "Texte / Chat"

def new_chat():
    st.session_state.user_input = ""
    st.session_state.selected_mode = "Texte / Chat"

st.sidebar.button("✏️ Nouvelle discussion", on_click=new_chat, use_container_width=True)

# ---------------------------------------------------------
# EN-TÊTE ET BIENVENUE
# ---------------------------------------------------------
st.title("🤖 Boblin AI")

st.write(f"Bonjour **{user_name}** ! Je suis **Boblin AI**, votre assistant virtuel. Que souhaitez-vous faire aujourd'hui ?")

# Code Adsterra officiel
adsterra_code = """
<script async="async" data-cfasync="false" src="https://pl31362196.profitableratecpmnetwork.com/9c55e3342fc4121417b9d5bc6db0edfc/invoke.js"></script>
<div id="container-9c55e3342fc4121417b9d5bc6db0edfc"></div>
"""
components.html(adsterra_code, height=100)

system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle interactif, similaire à ChatGPT ou Gemini. "
    "Ton nom est Boblin AI. Si l'utilisateur te demande qui tu es, explique clairement que tu es Boblin AI, "
    "une intelligence artificielle créée pour l'aider à répondre à ses questions, rédiger du texte et générer/modifier des images."
)

# ---------------------------------------------------------
# FONCTIONNALITÉS
# ---------------------------------------------------------
if api_keys_list:
    mode = st.radio(
        "Choisissez une fonctionnalité :", 
        ["Texte / Chat", "Générer une Image", "Modifier une Image", "Mon Historique"],
        key="selected_mode"
    )

    # 1. TEXTE / CHAT (Barre de message fixée en bas grâce à st.chat_input)
    if mode == "Texte / Chat":
        # Affichage de l'historique de la discussion active
        chat_history_data = get_full_chat_context(user_email)
        for msg in chat_history_data:
            role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(role):
                st.write(msg["parts"][0]["text"])

        # Si l'utilisateur a cliqué sur "Continuer cette discussion" depuis l'historique
        initial_val = st.session_state.user_input if st.session_state.user_input else None

        # st.chat_input reste toujours ancré en bas de page
        user_prompt = st.chat_input("Posez votre question à Boblin AI...")

        if user_prompt:
            st.session_state.user_input = ""
            with st.chat_message("user"):
                st.write(user_prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Boblin AI réfléchit..."):
                    try:
                        chat_history = get_full_chat_context(user_email)
                        chat_history.append({"role": "user", "parts": [{"text": user_prompt}]})
                        
                        def call_chat(client):
                            return generate_text_smart(client, chat_history, system_instruction)
                            
                        response = execute_with_key_rotation(call_chat)
                        st.write(response.text)
                        
                        save_to_history(user_email, user_prompt, response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    # 2. GÉNÉRATION IMAGE
    elif mode == "Générer une Image":
        st.subheader("🖼️ Création d'Image HD")
        image_prompt = st.text_area("Décrivez l'image à générer :", placeholder="Un paysage futuriste, net, 8k...")
        
        if st.button("Générer l'Image", type="primary"):
            if image_prompt.strip():
                with st.spinner("Boblin AI génère votre image..."):
                    try:
                        def call_image_generation(client):
                            return client.models.generate_images(
                                model="imagen-3.0-generate-002",
                                prompt=image_prompt,
                                config=types.GenerateImagesConfig(
                                    number_of_images=1,
                                    aspect_ratio="1:1"
                                )
                            )
                        
                        result = execute_with_key_rotation(call_image_generation)
                        for generated_image in result.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            st.image(image_bytes, use_container_width=True)
                            
                        save_to_history(user_email, f"[Image] {image_prompt}", "Image générée et affichée avec succès.")
                    except Exception as e:
                        try:
                            def call_fallback_gen(client):
                                return generate_text_smart(client, f"Génère ou décris de façon ultra-visuelle l'image suivante : {image_prompt}", system_instruction)
                            res = execute_with_key_rotation(call_fallback_gen)
                            st.write(res.text)
                            save_to_history(user_email, f"[Image] {image_prompt}", res.text)
                        except Exception as inner_e:
                            st.error(f"Erreur : {inner_e}")
            else:
                st.warning("Veuillez décrire l'image.")

    # 3. MODIFICATION / ANALYSE D'IMAGE
    elif mode == "Modifier une Image":
        st.subheader("🎨 Retouche et Modification d'Image")
        uploaded_image = st.file_uploader("Téléchargez l'image à modifier :", type=["jpg", "jpeg", "png", "webp"])
        edit_prompt = st.text_area("Votre consigne de modification :", placeholder="Ex: Change l'arrière-plan en un coucher de soleil...")

        if st.button("Modifier l'image", type="primary"):
            if uploaded_image and edit_prompt.strip():
                with st.spinner("Boblin AI traite et modifie votre image..."):
                    try:
                        image = Image.open(uploaded_image)
                        
                        def call_vision_edit(client):
                            return generate_text_smart(
                                client, 
                                [
                                    f"En tant qu'IA experte en retouche d'image, réponds à cette consigne de modification ou décris précisément les changements apportés sur cette image : {edit_prompt}", 
                                    image
                                ], 
                                system_instruction
                            )
                            
                        response = execute_with_key_rotation(call_vision_edit)
                        st.subheader("Résultat de Boblin AI :")
                        st.image(image, caption="Image originale", use_container_width=True)
                        st.write(response.text)
                        
                        save_to_history(user_email, f"[Modification Image] {edit_prompt}", response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")
            else:
                st.warning("Veuillez importer une image et écrire une consigne.")

    # 4. MON HISTORIQUE
    elif mode == "Mon Historique":
        st.subheader(f"📜 Historique de {user_name}")
        history_data = get_user_history(user_email)
        
        if history_data:
            for idx, item in enumerate(history_data):
                p, r, t = item
                with st.expander(f"🕒 {t} - {p[:40]}..."):
                    st.markdown(f"**Vous :** {p}")
                    st.markdown(f"**Boblin AI :** {r}")
                    
                    if st.button(f"💬 Continuer cette conversation", key=f"continue_{idx}"):
                        st.session_state.user_input = p
                        st.session_state.selected_mode = "Texte / Chat"
                        st.rerun()
        else:
            st.info("Aucun historique trouvé pour ce compte. Connectez-vous avec votre e-mail dans le menu de gauche.")

    st.markdown("---")
    components.html(adsterra_code, height=100)
else:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit.")
