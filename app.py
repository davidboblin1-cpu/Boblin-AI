import streamlit as st
import streamlit.components.v1 as components
from google import genai
import sqlite3
from datetime import datetime
import uuid

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# STYLE CSS : MODE NOIR + MASQUAGE TOTAL DU BADGE STREAMLIT
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Forcer le fond noir et texte blanc */
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Masque complètement le logo / badge flottant Streamlit en bas à droite */
        [data-testid="stStatusWidget"] {visibility: hidden; display: none;}
        div[class*="viewerBadge"] {visibility: hidden; display: none;}
        .styles_viewerBadge__1yG5_ {visibility: hidden; display: none;}

        /* Bannière du haut épinglée */
        .top-banner-fixed {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 999999;
            background-color: #0e1117;
            text-align: center;
            padding-top: 5px;
        }

        /* Bannière du bas épinglée */
        .bottom-banner-fixed {
            position: fixed;
            bottom: 70px;
            left: 0;
            width: 100%;
            z-index: 999999;
            background-color: #0e1117;
            text-align: center;
            padding: 5px 0;
        }

        /* Marges pour éviter que le contenu ne passe sous les pubs */
        .block-container {
            padding-top: 100px !important;
            padding-bottom: 160px !important;
        }
        
        p, h1, h2, h3, h4, h5, h6, span, label {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

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
# CODE DES BANNIÈRES ADSTERRA (HAUT & BAS)
# ---------------------------------------------------------
adsterra_code = """
<script async="async" data-cfasync="false" src="https://pl31362196.profitableratecpmnetwork.com/9c55e3342fc4121417b9d5bc6db0edfc/invoke.js"></script>
<div id="container-9c55e3342fc4121417b9d5bc6db0edfc"></div>
"""

# 1. Bannière du HAUT épinglée
st.markdown('<div class="top-banner-fixed">', unsafe_allow_html=True)
components.html(adsterra_code, height=55)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# BARRE DE NAVIGATION SUPÉRIEURE
# ---------------------------------------------------------
col_hist, col_title, col_git, col_new = st.columns([1, 2, 1, 1])

with col_hist:
    if st.button("🕒", help="Voir mon historique", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

with col_title:
    st.markdown("<h4 style='text-align: center; margin: 0; color: white;'>🤖 Boblin AI</h4>", unsafe_allow_html=True)

with col_git:
    st.markdown("""
        <a href="https://github.com/votre-nom-utilisateur/votre-repo" target="_blank" style="text-decoration: none;">
            <button style="width: 100%; background-color: #262730; color: white; border: 1px solid #4f4f4f; border-radius: 4px; padding: 4px; cursor: pointer;">
                🐱 GitHub
            </button>
        </a>
    """, unsafe_allow_html=True)

with col_new:
    if st.button("✏️", help="Nouvelle discussion", use_container_width=True):
        st.session_state.show_history = False
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# CHARGEMENT DES CLÉS API ET CORPS DE L'APPLICATION
# ---------------------------------------------------------
api_keys_list = [k.strip() for i in range(1, 16) if (k := st.secrets.get(f"GEMINI_API_KEY{i}", ""))]
if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

if api_keys_list:
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

        # 2. Bannière du BAS épinglée juste au-dessus du champ de chat
        st.markdown('<div class="bottom-banner-fixed">', unsafe_allow_html=True)
        components.html(adsterra_code, height=55)
        st.markdown('</div>', unsafe_allow_html=True)

        user_prompt = st.chat_input("Posez votre question à Boblin AI...")

        if user_prompt:
            with st.chat_message("user"):
                st.write(user_prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Boblin AI réfléchit..."):
                    try:
                        chat_history = get_full_chat_context(current_user)
                        chat_history.append({"role": "user", "parts": [{"text": user_prompt}]})
                        
                        client = genai.Client(api_key=api_keys_list[0])
                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=chat_history,
                            config={"system_instruction": system_instruction}
                        )
                        st.write(response.text)
                        save_to_history(current_user, user_prompt, response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

else:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit.")
