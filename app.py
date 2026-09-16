import streamlit as st
import streamlit.components.v1 as components
from google import genai
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered")

# ---------------------------------------------------------
# STYLE CSS POUR MASQUER LE MENU STREAMLIT (FORK, GITHUB, 3 POINTS)
# ---------------------------------------------------------
st.markdown("""
    <style>
        /* Masque complètement le menu hamburger en haut à droite, le pied de page et les options GitHub */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Style des boutons du haut pour un look application mobile moderne */
        .top-btn {
            background-color: transparent;
            border: none;
            color: #ffffff;
            font-size: 20px;
            cursor: pointer;
            text-align: center;
            padding: 5px;
        }
    </style>
""", unsafe_allow_html=True)

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
# GESTION DE L'ÉTAT DE LA SESSION
# ---------------------------------------------------------
if "show_history" not in st.session_state:
    st.session_state.show_history = False

user_email = "Invite"
user_name = "Visiteur"
try:
    if hasattr(st, "user") and st.user and getattr(st.user, "email", None):
        user_email = st.user.email
        user_name = getattr(st.user, "name", user_email.split("@")[0])
    elif "custom_user_email" in st.session_state and st.session_state.custom_user_email:
        user_email = st.session_state.custom_user_email
        user_name = user_email.split("@")[0]
except Exception:
    pass

# Optionnel : configuration rapide de l'email dans la sidebar cachée
with st.sidebar:
    input_email = st.text_input("Votre e-mail :", value=user_email if user_email != "Invite" else "", placeholder="exemple@email.com")
    if input_email.strip():
        st.session_state.custom_user_email = input_email.strip()

system_instruction = (
    "Tu es Boblin AI, un modèle d'intelligence artificielle textuel interactif, similaire à ChatGPT ou Gemini. "
    "Ton nom est Boblin AI. Si l'utilisateur te demande qui tu es, explique clairement que tu es Boblin AI, "
    "une intelligence artificielle créée pour l'aider à répondre à ses questions et rédiger du texte."
)

# ---------------------------------------------------------
# BARRE DE NAVIGATION SUPÉRIEURE (HISTORIQUE À GAUCHE / CRAYON À DROITE)
# ---------------------------------------------------------
col_left, col_title, col_right = st.columns([1, 2.5, 1])

with col_left:
    if st.button("🕒", help="Voir l'historique", use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

with col_title:
    st.markdown("<h3 style='text-align: center; margin: 0;'>🤖 Boblin AI</h3>", unsafe_allow_html=True)

with col_right:
    if st.button("✏️", help="Nouvelle discussion", use_container_width=True):
        st.session_state.show_history = False
        st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# AFFICHAGE PRINCIPAL (OU HISTORIQUE OU CHAT)
# ---------------------------------------------------------
if api_keys_list := [
    k.strip() for i in range(1, 16) if (k := st.secrets.get(f"GEMINI_API_KEY{i}", ""))
]:
    pass
else:
    # Récupération de secours des clés
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
    api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

if api_keys_list:
    # Bannière Adsterra du Haut
    adsterra_code = """
    <script async="async" data-cfasync="false" src="https://pl31362196.profitableratecpmnetwork.com/9c55e3342fc4121417b9d5bc6db0edfc/invoke.js"></script>
    <div id="container-9c55e3342fc4121417b9d5bc6db0edfc"></div>
    """
    components.html(adsterra_code, height=90)

    if st.session_state.show_history:
        # VUE HISTORIQUE
        st.subheader(f"📜 Historique de {user_name}")
        history_data = get_user_history(user_email)
        
        if history_data:
            for idx, item in enumerate(history_data):
                p, r, t = item
                with st.expander(f"🕒 {t} - {p[:40]}..."):
                    st.markdown(f"**Vous :** {p}")
                    st.markdown(f"**Boblin AI :** {r}")
                    if st.button(f"💬 Reprendre", key=f"continue_{idx}"):
                        st.session_state.show_history = False
                        st.rerun()
        else:
            st.info("Aucun historique trouvé pour ce compte.")
            
    else:
        # VUE CHAT CLASSIQUE
        chat_history_data = get_full_chat_context(user_email)
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
                        chat_history = get_full_chat_context(user_email)
                        chat_history.append({"role": "user", "parts": [{"text": user_prompt}]})
                        
                        # Logique simple d'appel modèle
                        client = genai.Client(api_key=api_keys_list[0])
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=chat_history,
                            config={"system_instruction": system_instruction}
                        )
                        st.write(response.text)
                        save_to_history(user_email, user_prompt, response.text)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    # Bannière Adsterra du Bas
    st.markdown("---")
    components.html(adsterra_code, height=90)
else:
    st.info("Veuillez ajouter vos clés API dans les Secrets de Streamlit.")
