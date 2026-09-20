from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import streamlit.components.v1 as components
from google import genai
import urllib.parse

# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Boblin AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
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
# WATERMARK
# =========================================================

def add_watermark(image_url, watermark_text="BOBLIN AI"):
    try:
        response = requests.get(image_url, timeout=30)
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        width, height = img.size

        overlay = Image.new(
            "RGBA",
            img.size,
            (255, 255, 255, 0)
        )

        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        bbox = draw.textbbox(
            (0, 0),
            watermark_text,
            font=font
        )

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        padding_x = 12
        padding_y = 7

        margin_right = int(width * 0.025)
        margin_bottom = int(height * 0.025)

        x2 = width - margin_right
        y2 = height - margin_bottom

        x1 = x2 - text_width - padding_x * 2
        y1 = y2 - text_height - padding_y * 2

        # Ombre
        draw.rounded_rectangle(
            [
                x1 + 3,
                y1 + 4,
                x2 + 3,
                y2 + 4
            ],
            radius=12,
            fill=(0, 0, 0, 100)
        )

        # Badge
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=12,
            fill=(10, 10, 15, 205),
            outline=(120, 90, 255, 180),
            width=1
        )

        draw.text(
            (
                x1 + padding_x,
                y1 + padding_y
            ),
            watermark_text,
            fill=(255, 255, 255, 245),
            font=font
        )

        final = Image.alpha_composite(
            img,
            overlay
        )

        return final.convert("RGB")

    except Exception:
        return image_url


# =========================================================
# CSS PREMIUM 3D
# =========================================================

st.markdown(
    """
<style>

/* ==============================
   GLOBAL
============================== */

html, body, [class*="css"] {
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(91, 60, 180, 0.20),
            transparent 28%
        ),
        radial-gradient(
            circle at 85% 80%,
            rgba(0, 180, 255, 0.10),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            #050509 0%,
            #090912 45%,
            #050507 100%
        );

    color: white;
}

/* ==============================
   REMOVE STREAMLIT HEADER
============================== */

header[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* ==============================
   MAIN CONTAINER
============================== */

.block-container {
    max-width: 1250px;
    padding-top: 25px;
    padding-bottom: 100px;
}

/* ==============================
   SIDEBAR
============================== */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(15, 15, 25, 0.98),
            rgba(5, 5, 10, 0.98)
        ) !important;

    border-right:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        10px 0 40px rgba(0,0,0,0.45);
}

/* ==============================
   SIDEBAR TITLE
============================== */

.sidebar-logo {
    padding: 18px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(100,70,255,0.20),
            rgba(20,20,30,0.65)
        );

    border:
        1px solid rgba(130,100,255,0.25);

    box-shadow:
        inset 0 1px rgba(255,255,255,0.10),
        0 15px 40px rgba(0,0,0,0.30);

    margin-bottom: 20px;
}

.sidebar-logo-title {
    font-size: 22px;
    font-weight: 800;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #9d8cff,
            #ffffff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-logo-sub {
    font-size: 12px;
    color: #888 !important;
    margin-top: 4px;
}

/* ==============================
   TOP BAR
============================== */

.topbar {
    position: relative;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 15px 20px;

    margin-bottom: 25px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(25,25,38,0.92),
            rgba(10,10,16,0.82)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 20px 60px rgba(0,0,0,0.40),
        inset 0 1px rgba(255,255,255,0.08);

    backdrop-filter: blur(20px);
}

/* ==============================
   LOGO
============================== */

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    width: 45px;
    height: 45px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 14px;

    background:
        linear-gradient(
            145deg,
            #7657ff,
            #241b4f
        );

    box-shadow:
        0 8px 25px rgba(100,70,255,0.45),
        inset 0 1px rgba(255,255,255,0.30);

    font-size: 23px;
}

.logo-title {
    font-size: 20px;
    font-weight: 800;
}

.logo-subtitle {
    font-size: 11px;
    color: #777 !important;
}

/* ==============================
   HERO
============================== */

.hero {
    position: relative;

    padding: 55px 35px;

    margin-bottom: 28px;

    border-radius: 30px;

    background:
        radial-gradient(
            circle at 20% 20%,
            rgba(119,80,255,0.25),
            transparent 35%
        ),
        radial-gradient(
            circle at 80% 70%,
            rgba(0,190,255,0.12),
            transparent 35%
        ),
        linear-gradient(
            145deg,
            rgba(25,25,40,0.95),
            rgba(8,8,14,0.90)
        );

    border:
        1px solid rgba(255,255,255,0.09);

    box-shadow:
        0 30px 80px rgba(0,0,0,0.50),
        inset 0 1px rgba(255,255,255,0.10);

    overflow: hidden;
}

/* Decorative glow */

.hero::before {
    content: "";

    position: absolute;

    width: 300px;
    height: 300px;

    right: -120px;
    top: -140px;

    background: #745cff;

    filter: blur(100px);

    opacity: 0.18;
}

.hero h1 {
    position: relative;

    font-size: clamp(35px, 5vw, 60px);

    line-height: 1;

    margin-bottom: 15px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #a594ff,
            #ffffff
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    position: relative;

    max-width: 650px;

    color: #9b9ba8 !important;

    font-size: 15px;

    line-height: 1.7;
}

/* ==============================
   3D CARDS
============================== */

.ai-card {
    position: relative;

    padding: 22px;

    min-height: 145px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(30,30,45,0.90),
            rgba(10,10,17,0.90)
        );

    border:
        1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 18px 40px rgba(0,0,0,0.38),
        inset 0 1px rgba(255,255,255,0.08);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;

    overflow: hidden;
}

.ai-card:hover {
    transform:
        translateY(-7px)
        perspective(800px)
        rotateX(2deg);

    box-shadow:
        0 30px 60px rgba(0,0,0,0.55),
        0 0 35px rgba(110,80,255,0.12);
}

.ai-card-icon {
    font-size: 30px;

    margin-bottom: 12px;
}

.ai-card-title {
    font-size: 16px;
    font-weight: 750;
}

.ai-card-text {
    color: #858592 !important;
    font-size: 12px;
    margin-top: 5px;
}

/* ==============================
   CHAT MESSAGES
============================== */

[data-testid="stChatMessage"] {
    background:
        linear-gradient(
            145deg,
            rgba(22,22,32,0.92),
            rgba(10,10,16,0.88)
        ) !important;

    border:
        1px solid rgba(255,255,255,0.07) !important;

    border-radius: 20px !important;

    padding: 15px !important;

    margin-bottom: 14px !important;

    box-shadow:
        0 15px 35px rgba(0,0,0,0.25),
        inset 0 1px rgba(255,255,255,0.05);

    backdrop-filter: blur(15px);
}

/* ==============================
   CHAT INPUT
============================== */

[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] > div {
    background:
        linear-gradient(
            145deg,
            rgba(25,25,38,0.96),
            rgba(10,10,16,0.96)
        ) !important;

    border:
        1px solid rgba(130,100,255,0.30) !important;

    border-radius: 20px !important;

    box-shadow:
        0 15px 50px rgba(0,0,0,0.45),
        0 0 30px rgba(100,70,255,0.08);

    backdrop-filter: blur(20px);
}

[data-testid="stChatInput"] textarea {
    color: white !important;

    -webkit-text-fill-color: white !important;

    background: transparent !important;
}

/* ==============================
   BUTTONS
============================== */

.stButton > button {
    border-radius: 13px !important;

    border:
        1px solid rgba(255,255,255,0.08) !important;

    background:
        linear-gradient(
            145deg,
            rgba(35,35,50,0.95),
            rgba(15,15,23,0.95)
        ) !important;

    color: white !important;

    box-shadow:
        0 8px 20px rgba(0,0,0,0.30),
        inset 0 1px rgba(255,255,255,0.08);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);

    box-shadow:
        0 12px 28px rgba(0,0,0,0.40),
        0 0 20px rgba(100,70,255,0.15);
}

/* ==============================
   EXPANDER
============================== */

[data-testid="stExpander"] {
    border:
        1px solid rgba(255,255,255,0.08) !important;

    border-radius: 18px !important;

    background:
        rgba(15,15,23,0.75) !important;

    box-shadow:
        0 15px 35px rgba(0,0,0,0.25);
}

/* ==============================
   IMAGES
============================== */

[data-testid="stImage"] img {
    border-radius: 18px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.45);

    border:
        1px solid rgba(255,255,255,0.08);
}

/* ==============================
   STATUS BADGE
============================== */

.status {
    display: inline-flex;

    align-items: center;

    gap: 7px;

    padding: 7px 12px;

    border-radius: 999px;

    background:
        rgba(50,200,120,0.08);

    border:
        1px solid rgba(50,200,120,0.18);

    color: #69e6a2;

    font-size: 11px;
}

.status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #49dc8a;

    box-shadow:
        0 0 10px #49dc8a;
}

/* ==============================
   SCROLLBAR
============================== */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: #050509;
}

::-webkit-scrollbar-thumb {
    background: #29253d;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #51468a;
}

/* ==============================
   TEXT
============================== */

p, span, label, div, h1, h2, h3, h4 {
    color: white;
}

small {
    color: #777 !important;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-logo-title">
                🤖 Boblin AI
            </div>

            <div class="sidebar-logo-sub">
                AI Creative Studio
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### ⚡ Studio")

    st.markdown(
        """
        <div style="
            padding:12px;
            border-radius:14px;
            background:rgba(255,255,255,0.035);
            border:1px solid rgba(255,255,255,0.06);
            margin-bottom:10px;
        ">
        💬 <b>Chat intelligent</b><br>
        <small>Discute avec Boblin AI</small>
        </div>

        <div style="
            padding:12px;
            border-radius:14px;
            background:rgba(255,255,255,0.035);
            border:1px solid rgba(255,255,255,0.06);
            margin-bottom:10px;
        ">
        🎨 <b>Génération d'images</b><br>
        <small>Crée tes visuels</small>
        </div>

        <div style="
            padding:12px;
            border-radius:14px;
            background:rgba(255,255,255,0.035);
            border:1px solid rgba(255,255,255,0.06);
        ">
        🎬 <b>Animations</b><br>
        <small>Transforme tes idées</small>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    if API_KEYS:
        st.markdown(
            f"""
            <div class="status">
                <div class="status-dot"></div>
                {len(API_KEYS)} clé(s) API active(s)
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("Aucune clé Gemini détectée.")

    st.markdown("---")

    st.markdown("### 📢 Publicité")

    ADSTERRA_CODE = """
    <div style="text-align:center;width:100%;overflow:hidden;">
        <script
        type="text/javascript"
        src="https://pl31374844.profitableratecpmnetwork.com/39/7e/35/397e35bae2ba969d0705ae639056c3d5.js">
        </script>

        <script
        async="async"
        data-cfasync="false"
        src="https://pl31374842.profitableratecpmnetwork.com/401a9c1e01727dd7d19700ecaaf3b03d/invoke.js">
        </script>

        <div id="container-401a9c1e01727dd7d19700ecaaf3b03d"></div>
    </div>
    """

    components.html(
        ADSTERRA_CODE,
        height=300,
        scrolling=False
    )

# =========================================================
# TOP BAR
# =========================================================

col1, col2 = st.columns([5, 1], vertical_alignment="center")

with col1:
    st.markdown(
        """
        <div class="topbar">

            <div class="logo">

                <div class="logo-icon">
                    🤖
                </div>

                <div>
                    <div class="logo-title">
                        Boblin AI
                    </div>

                    <div class="logo-subtitle">
                        Creative Intelligence Studio
                    </div>
                </div>

            </div>

            <div class="status">
                <div class="status-dot"></div>
                ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if st.button("＋ Nouveau", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "✨ Nouvelle session prête. "
                "Que veux-tu créer aujourd'hui ?"
            )
        }]
        st.rerun()

# =========================================================
# INITIALISATION CHAT
# =========================================================

default_welcome = (
    "👋 **Bienvenue sur Boblin AI Studio.**\n\n"
    "Je peux discuter avec toi, analyser des textes, "
    "créer des images et transformer tes idées en concepts visuels."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": default_welcome
    }]

# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            Crée.<br>
            Imagine.<br>
            <span>Amplifie.</span>
        </h1>

        <p>
            Ton espace créatif propulsé par l'intelligence artificielle.
            Discute avec Boblin, génère des images et transforme tes idées
            en créations visuelles.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# QUICK CARDS
# =========================================================

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-card-icon">💬</div>

            <div class="ai-card-title">
                Assistant IA
            </div>

            <div class="ai-card-text">
                Questions, idées, rédaction et analyse.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-card-icon">🎨</div>

            <div class="ai-card-title">
                Image Studio
            </div>

            <div class="ai-card-text">
                Génère des visuels à partir de tes descriptions.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="ai-card">

            <div class="ai-card-icon">🎬</div>

            <div class="ai-card-title">
                Motion Studio
            </div>

            <div class="ai-card-text">
                Transforme une idée en concept animé.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# FILE UPLOAD
# =========================================================

with st.expander(
    "📎 Ajouter une image à analyser ou modifier",
    expanded=False
):

    uploaded_file = st.file_uploader(
        "Choisir une image",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

uploaded_image_pil = None

if uploaded_file:
    uploaded_image_pil = Image.open(uploaded_file)

    st.image(
        uploaded_image_pil,
        caption="Image prête",
        width=220
    )

# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message.get("type") == "image":

            if message.get("input_image"):
                st.image(
                    message["input_image"],
                    width=180,
                    caption="Image originale"
                )

            st.image(
                message["content"],
                caption=message.get("caption")
            )

        elif message.get("type") == "animation":

            st.image(
                message["content"],
                caption=message.get("caption"),
                use_container_width=True
            )

        else:
            st.markdown(message["content"])

# =========================================================
# USER INPUT
# =========================================================

prompt = st.chat_input(
    "✨ Écris une idée, une question ou demande une création..."
)

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):

        if uploaded_image_pil:
            st.image(
                uploaded_image_pil,
                width=180
            )

        st.markdown(prompt)

    if not client:

        st.error(
            "⚠️ Client Gemini non initialisé. "
            "Vérifie tes secrets Streamlit."
        )

    else:

        prompt_lower = prompt.lower()

        # -------------------------------------------------
        # DETECTION
        # -------------------------------------------------

        is_video_request = any(
            word in prompt_lower
            for word in [
                "video",
                "tiktok",
                "reel",
                "animation",
                "animé",
                "anime",
                "moving",
                "motion"
            ]
        )

        is_image_request = (
            uploaded_image_pil is not None
            or any(
                word in prompt_lower
                for word in [
                    "image",
                    "dessin",
                    "photo",
                    "create",
                    "generate",
                    "génère",
                    "créer",
                    "modifier",
                    "modifier",
                    "changer",
                    "afro"
                ]
            )
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        with st.chat_message("assistant"):

            response_success = False
            attempts = 0
            max_attempts = len(API_KEYS)

            while (
                not response_success
                and attempts < max_attempts
            ):

                try:

                    if attempts > 0:

                        st.session_state.api_key_index += 1

                        client, _ = get_rotating_client()

                    # =====================================
                    # VIDEO / ANIMATION
                    # =====================================

                    if is_video_request:

                        with st.spinner(
                            "🎬 Boblin prépare ton concept..."
                        ):

                            result = client.models.generate_content(

                                model="gemini-3.6-flash",

                                contents=(
                                    "Create a cinematic vertical 9:16 "
                                    "animation prompt based on this request: "
                                    f"'{prompt}'. "
                                    "Return ONLY the English prompt."
                                )
                            )

                            clean_prompt = result.text.strip()

                            encoded_prompt = urllib.parse.quote(
                                clean_prompt
                            )

                            animation_url = (
                                "https://pollinations.ai/p/"
                                f"{encoded_prompt}"
                                "?width=540"
                                "&height=960"
                                "&model=flux"
                                "&seed=42"
                                "&nologo=false"
                            )

                            st.image(
                                animation_url,
                                caption=prompt,
                                use_container_width=True
                            )

                            st.session_state.messages.append({
                                "role": "assistant",
                                "type": "animation",
                                "content": animation_url,
                                "caption": prompt
                            })

                            response_success = True

                    # =====================================
                    # IMAGE
                    # =====================================

                    elif is_image_request:

                        with st.spinner(
                            "🎨 Boblin crée ton image..."
                        ):

                            if uploaded_image_pil:

                                result = client.models.generate_content(

                                    model="gemini-3.6-flash",

                                    contents=[
                                        uploaded_image_pil,

                                        (
                                            "Analyze this image and the "
                                            "user's editing instruction: "
                                            f"'{prompt}'. "
                                            "Create a detailed professional "
                                            "English image generation prompt "
                                            "for the modified image. "
                                            "Return ONLY the prompt."
                                        )
                                    ]
                                )

                            else:

                                result = client.models.generate_content(

                                    model="gemini-3.6-flash",

                                    contents=(
                                        "Create an ultra-realistic, "
                                        "professional image generation "
                                        "prompt based on: "
                                        f"'{prompt}'. "
                                        "Return ONLY the English prompt."
                                    )
                                )

                            clean_prompt = result.text.strip()

                            encoded_prompt = urllib.parse.quote(
                                clean_prompt
                            )

                            image_url = (
                                "https://image.pollinations.ai/prompt/"
                                f"{encoded_prompt}"
                                "?width=1024"
                                "&height=1024"
                                "&nologo=true"
                                "&private=true"
                                "&model=flux"
                            )

                            final_image = add_watermark(
                                image_url,
                                "BOBLIN AI"
                            )

                            if uploaded_image_pil:

                                st.image(
                                    uploaded_image_pil,
                                    width=180,
                                    caption="Original"
                                )

                            st.image(
                                final_image,
                                caption=prompt
                            )

                            st.session_state.messages.append({

                                "role": "assistant",

                                "type": "image",

                                "content": final_image,

                                "caption": prompt,

                                "input_image": (
                                    uploaded_image_pil
                                    if uploaded_image_pil
                                    else None
                                )
                            })

                            response_success = True

                    # =====================================
                    # CHAT
                    # =====================================

                    else:

                        with st.spinner(
                            "🧠 Boblin réfléchit..."
                        ):

                            system_instruction = (
                                "You are Boblin AI, a helpful, "
                                "friendly and intelligent assistant. "
                                "Respond in French. "
                                "Use clean formatting and Markdown. "
                                "Be concise unless the user requests "
                                "a detailed explanation."
                            )

                            history = ""

                            for msg in st.session_state.messages[-8:]:

                                if (
                                    "content" in msg
                                    and isinstance(
                                        msg["content"],
                                        str
                                    )
                                ):

                                    role = (
                                        "User"
                                        if msg["role"] == "user"
                                        else "Assistant"
                                    )

                                    history += (
                                        f"{role}: "
                                        f"{msg['content']}\n"
                                    )

                            full_context = (

                                f"{system_instruction}\n\n"

                                f"Conversation:\n"
                                f"{history}\n"

                                f"New question:\n"
                                f"{prompt}"
                            )

                            response = (
                                client.models.generate_content(
                                    model="gemini-3.6-flash",
                                    contents=full_context
                                )
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

                        st.error(
                            "❌ Toutes les clés API disponibles "
                            "ont échoué. Ajoute de nouvelles clés "
                            "dans les Secrets Streamlit."
                        )
