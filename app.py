import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import io
import sqlite3
from datetime import datetime
import uuid
import urllib.parse
import urllib.request

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
                if "429" in error_str or "503" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower() or "unavailable" in error_str.lower():
                    st.session_state.key_index = (st.session_state.key_index + 1) % num_keys
                    if attempt == num_keys - 1:
                        raise Exception("Les serveurs Gemini sont saturés. Veuillez patienter un instant.")
                else:
                    raise e
        raise Exception("Erreur de rotation des clés.")

    # -----------------------------------------------------
    # MODE 1 : STUDIO IMAGE
    # -----------------------------------------------------
    if app_mode == "🎨 Studio Image":
        st.markdown("### 🎨 Studio Image & Animation")
        st.caption("Générez une image ou transformez votre idée directement en mode animé.")

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
                        refined_prompt = ""
                        try:
                            if uploaded_file:
                                contents = [
                                    input_image, 
                                    f"Rédige un prompt descriptif ultra-détaillé en anglais pour transformer cette image selon : {image_prompt}. Réponds uniquement avec le prompt en anglais."
                                ]
                            else:
                                contents = f"Rédige un prompt descriptif ultra-détaillé en anglais pour : {image_prompt}. Réponds uniquement avec le prompt en anglais."

                            response = call_gemini_with_rotation(contents, is_chat=False)
                            if response and hasattr(response, 'text'):
                                refined_prompt = response.text.strip()
                        except Exception:
                            refined_prompt = image_prompt + ", high quality anime style, highly detailed"

                        if not refined_prompt:
                            refined_prompt = image_prompt

                        encoded_prompt = urllib.parse.quote(refined_prompt)
                        image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42&nologo=true"
                        
                        req = urllib.request.Request(
                            image_url, 
                            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                        )
                        with urllib.request.urlopen(req) as response_img:
                            image_bytes = response_img.read()
                        
                        final_image = Image.open(io.BytesIO(image_bytes))
                        
                        st.success("Image générée avec succès !")
                        st.image(final_image, caption="✨ Résultat généré par Boblin AI", use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"Erreur de génération : {e}")

    # -----------------------------------------------------
    # MODE 2 : CHAT TEXTE (AVEC CONTRÔLE VOCAL COMPLET 🔊 / ⏹️)
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
            for msg_idx, msg in enumerate(chat_history_data):
                role = "user" if msg["role"] == "user" else "assistant"
                with st.chat_message(role):
                    msg_text = msg["parts"][0]["text"]
                    st.write(msg_text)
                    
                    if role == "assistant":
                        safe_hist_text = msg_text.replace('"', "'").replace('\n', ' ')
                        audio_id = f"hist_{msg_idx}"
                        hist_audio_html = f"""
                        <div style="margin-top: 8px; margin-bottom: 15px; display: flex; gap: 10px;">
                            <button onclick="lireTexte_{audio_id}()" style="background-color: #2e7d32; color: white; padding: 8px 14px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                🔊 Écouter
                            </button>
                            <button onclick="arreterTexte_{audio_id}()" style="background-color: #c62828; color: white; padding: 8px 14px; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                ⏹️ Arrêter
                            </button>
                        </div>
                        <script>
                        function getVoixFr_{audio_id}(synth) {{
                            var voices = synth.getVoices();
                            // Cherche en priorité une voix française propre (Google ou système)
                            for(var i = 0; i < voices.length; i++) {{
                                if(voices[i].lang.includes('fr') || voices[i].lang.includes('FR')) {{
                                    return voices[i];
                                }}
                            }}
                            return null;
                        }}
                        function lireTexte_{audio_id}() {{
                            if ('speechSynthesis' in window) {{
                                var synth = window.speechSynthesis;
                                synth.cancel();
                                var msg = new SpeechSynthesisUtterance("{safe_hist_text}");
                                msg.rate = 0.95;
                                
                                var voixChoisie = getVoixFr_{audio_id}(synth);
                                if(voixChoisie) {{ msg.voice = voixChoisie; }}
                                
                                synth.speak(msg);
                            }}
                        }}
                        function arreterTexte_{audio_id}() {{
                            if ('speechSynthesis' in window) {{
                                window.speechSynthesis.cancel();
                            }}
                        }}
                        </script>
                        """
                        components.html(hist_audio_html, height=55)

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
                            ai_response_text = response.text
                            
                            st.write(ai_response_text)
                            save_to_history(current_user, user_prompt, ai_response_text)

                            texte_securise = ai_response_text.replace('"', "'").replace('\n', ' ')
                            voix_html = f"""
                            <div style="margin-top: 15px; margin-bottom: 25px; display: flex; gap: 12px;">
                                <button onclick="lireTexteNouveau()" style="background-color: #2e7d32; color: white; padding: 12px 18px; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; font-weight: bold; flex: 1; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                                    🔊 Écouter (Audio)
                                </button>
                                <button onclick="arreterTexteNouveau()" style="background-color: #c62828; color: white; padding: 12px 18px; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; font-weight: bold; flex: 1; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                                    ⏹️ Arrêter
                                </button>
                            </div>
                            <script>
                            function getVoixFrActive(synth) {{
                                var voices = synth.getVoices();
                                for(var i = 0; i < voices.length; i++) {{
                                    if(voices[i].lang.includes('fr') || voices[i].lang.includes('FR')) {{
                                        return voices[i];
                                    }}
                                }}
                                return null;
                            }}
                            function lireTexteNouveau() {{
                                if ('speechSynthesis' in window) {{
                                    var synth = window.speechSynthesis;
                                    synth.cancel();
                                    var message = new SpeechSynthesisUtterance("{texte_securise}");
                                    message.rate = 0.95;
                                    
                                    var voixChoisie = getVoixFrActive(synth);
                                    if(voixChoisie) {{ message.voice = voixChoisie; }}
                                    
                                    synth.speak(message);
                                }} else {{
                                    alert("Désolé, votre navigateur ne supporte pas la lecture vocale.");
                                }}
                            }}
                            function arreterTexteNouveau() {{
                                if ('speechSynthesis' in window) {{
                                    window.speechSynthesis.cancel();
                                }}
                            }}
                            </script>
                            """
                            components.html(voix_html, height=75)

                        except Exception as e:
                            st.error(f"Erreur : {e}")

# Affichage du script additionnel en bas de page
st.markdown("---")
components.html(bottom_script_code, height=50)
st.markdown("---")
