from PIL import Image
from google import genai
import streamlit as st

st.set_page_config(page_title="Boblin AI", page_icon="🤖", layout="centered")

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #080914 !important;
    color: white !important;
}

header {
    background: transparent !important;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 720px;
    padding: 20px 18px 140px;
}

.boblin {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 20px;
    border-radius: 28px;
    background: linear-gradient(135deg, #25154d, #0d0d1b);
    border: 1px solid #7145d9;
}

.logo {
    width: 65px;
    height: 65px;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #8b45ff, #4d20c9);
    font-size: 30px;
}

.name {
    font-size: 27px;
    font-weight: 800;
}

.subtitle {
    color: #a99fc0;
    font-size: 12px;
    margin-top: 6px;
}

.online {
    margin-left: auto;
    padding: 9px 12px;
    border-radius: 20px;
    border: 1px solid #25d995;
    color: #43e59b;
    font-size: 11px;
    white-space: nowrap;
}

.dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: 6px;
    border-radius: 50%;
    background: #43e59b;
    box-shadow: 0 0 10px #43e59b;
}

.hero {
    margin-top: 25px;
    min-height: 430px;
    padding: 35px 25px;
    border-radius: 30px;
    background:
        radial-gradient(circle at 80% 75%, #45209a55, transparent 30%),
        linear-gradient(145deg, #1c1533, #090a16);
    border: 1px solid #7545df;
}

.hero h1 {
    font-size: 52px;
    line-height: .98;
    margin: 0 0 25px;
}

.hero .purple {
    color: #aa7cff;
}

.hero p {
    color: #aaa1c1;
    font-size: 16px;
    line-height: 1.7;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 15px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: calc(100% - 30px) !important;
    max-width: 680px !important;
}

[data-testid="stChatInput"] > div {
    background: #252231 !important;
    border: 1px solid #7545df !important;
    border-radius: 22px !important;
}

@media(max-width:600px) {
    .online {
        font-size: 9px;
        padding: 8px;
    }

    .name {
        font-size: 23px;
    }

    .hero h1 {
        font-size: 48px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# HEADER
st.markdown(
    """
<div class="boblin">

    <div class="logo">🤖</div>

    <div>
        <div class="name">Boblin AI</div>
        <div class="subtitle">
            Creative Intelligence Studio
        </div>
    </div>

    <div class="online">
        <span class="dot"></span>
        ONLINE
    </div>

</div>
""",
    unsafe_allow_html=True,
)


# UPLOAD
st.markdown("### 📸 Joindre une photo de devoir ou texte")

uploaded_file = st.file_uploader(
    "Choisir une image", type=["png", "jpg", "jpeg"], label_visibility="collapsed"
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, width=220)


# HERO
st.markdown(
    """
<div class="hero">

<h1>
Crée.<br>
<span class="purple">Imagine.</span><br>
Amplifie.
</h1>

<p>
Ton espace créatif propulsé par
l'intelligence artificielle.
Discute avec Boblin, génère des images
et transforme tes idées en créations visuelles.
</p>

</div>
""",
    unsafe_allow_html=True,
)


# GEMINI
API_KEY = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass


if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None


prompt = st.chat_input("Écris une idée, une question ou demande une création...")


if prompt:

    if client is None:

        st.error(
            "Clé Gemini introuvable. Ajoute GEMINI_API_KEY dans les Secrets"
            " Streamlit."
        )

    else:

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):

            try:

                response = client.models.generate_content(
                    model="gemini-3.6-flash", contents=prompt
                )

                st.markdown(response.text)

            except Exception as e:

                st.error("Erreur Gemini : " + str(e))
