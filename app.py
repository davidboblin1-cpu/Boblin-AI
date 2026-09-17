from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# --- FORCER LE THÈME SOMBRE DANS STREAMLIT ---
st.set_page_config(
    page_title="De Paul IA - Studio",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- RÉCUPÉRATION AUTOMATIQUE DE TOUTES LES CLÉS GEMINI_API_KEY ---
API_KEYS = []
try:
  for key_name in st.secrets:
    if key_name.startswith("GEMINI_API_KEY"):
      API_KEYS.append(st.secrets[key_name])
except Exception:
  API_KEYS = []


def get_rotating_client():
  """Gère la rotation automatique entre toutes les clés configurées"""
  if not API_KEYS:
    return None, None
  if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

  key = API_KEYS[st.session_state.api_key_index % len(API_KEYS)]
  try:
    return genai.Client(api_key=key), key
  except Exception:
    return None, key


client, current_key = get_rotating_client()


def add_watermark(image_url, watermark_text="boblin-ai"):
  """Télécharge l'image depuis l'URL et ajoute le texte 'boblin-ai' en bas à gauche"""
  try:
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    # Création d'un calque pour le texte pour gérer la transparence si besoin
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    width, height = img.size

    # Taille de police proportionnelle à la taille de l'image
    font_size = max(16, int(width * 0.035))
    try:
      # Utilisation d'une police par défaut ou standard
      font = ImageFont.load_default()
    except Exception:
      font = None

    # Position : en bas à gauche avec un léger padding
    x = int(width * 0.03)
    y = int(height - height * 0.07)

    # Dessiner un contour sombre pour que le texte soit lisible sur n'fomporte quel fond
    outline_color = (0, 0, 0, 220)
    text_color = (255, 255, 255, 230)

    # Effet de contour (ombre portée simple)
    for adj_x, adj_y in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
      draw.text(
          (x + adj_x, y + adj_y),
          watermark_text,
          fill=outline_color,
          font=font,
      )

    # Texte principal en blanc
    draw.text((x, y), watermark_text, fill=text_color, font=font)

    # Fusionner le calque de texte avec l'image originale
    watermarked = Image.alpha_composite(img, txt_layer)
    return watermarked.convert("RGB")
  except Exception:
    # En cas de problème de téléchargement, retourne l'URL d'origine
    return image_url


# --- CUSTOM CSS (FOND NOIR ET DESIGN PRO) ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117 !important;
    }
    .main {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    .stChatMessage {
        background-color: #161b22 !important;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
    }
    p, h1, h2, h3, h4, h5, h6, span, label, div {
        color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR & PUBLICITÉ ADSTERRA ---
with st.sidebar:
  st.markdown("### 🛠️ Menu De Paul IA")
  st.write(
      "Utilisez ce studio pour discuter, générer des images ou des animations"
      " dynamiques."
  )
  st.info(f"🔑 Clés API actives détectées : **{len(API_KEYS)}**")

  st.markdown("---")
  st.markdown("### 📢 Publicité")

  ADSTERRA_CODE = """
    <div style="text-align: center;">
        <script type="text/javascript" src="https://pl31374844.profitableratecpmnetwork.com/39/7e/35/397e35bae2ba969d0705ae639056c3d5.js"></script>
        <script async="async" data-cfasync="false" src="https://pl31374842.profitableratecpmnetwork.com/401a9c1e01727dd7d19700ecaaf3b03d/invoke.js"></script>
        <div id="container-401a9c1e01727dd7d19700ecaaf3b03d"></div>
    </div>
    """
  components.html(ADSTERRA_CODE, height=300)

# --- MESSAGE DE BIENVENUE FORCÉ EN FRANÇAIS ---
default_welcome = (
    "👋 Bonjour ! Je suis **De Paul IA**, votre assistant virtuel. Prêt à vous"
    " aider avec le modèle 3.6, analyser du texte, ou créer des"
    " images/animations. Que souhaitez-vous faire ?"
)
new_discussion_msg = (
    "✨ Nouvelle discussion commencée avec De Paul IA ! Comment puis-je vous"
    " aider ?"
)

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": default_welcome,
  }]

if not API_KEYS:
  st.error(
      "⚠️ Veuillez configurer vos clés API dans les Secrets de Streamlit"
      " (GEMINI_API_KEY1, GEMINI_API_KEY2, etc.)."
  )

# --- TOP NAVIGATION BAR ---
col_menu, col_title, col_new = st.columns([1, 3, 1], vertical_alignment="center")

with col_menu:
  if st.button("☰", help="Menu"):
    st.toast("De Paul IA Studio", icon="🤖")

with col_title:
  st.markdown(
      "<div style='text-align: center; font-weight: bold; color: white; font-"
      "size: 1.1rem;'>De Paul IA</div>",
      unsafe_allow_html=True,
  )

with col_new:
  if st.button("✏️", help="Nouvelle discussion"):
    st.session_state.messages = [{
        "role": "assistant",
        "content": new_discussion_msg,
    }]
    st.rerun()

st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #30363d;'>", unsafe_allow_html=True)

# --- ATTACHMENT OPTION ---
with st.expander("➕ Ajouter une photo ou un fichier (Optionnel)", expanded=False):
  uploaded_file = st.file_uploader(
      "Choisissez une image", type=["png", "jpg", "jpeg"]
  )

uploaded_image_pil = None
if uploaded_file is not None:
  uploaded_image_pil = Image.open(uploaded_file)
  st.image(
      uploaded_image_pil,
      caption="Photo prête pour modification",
      width=150,
  )

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("type") == "image":
      if message.get("input_image"):
        st.image(
            message["input_image"], width=150, caption="Photo originale"
        )
      st.image(message["content"], caption=message.get("caption"))
    elif message.get("type") == "animation":
      st.image(
          message["content"],
          caption=message.get("caption"),
          use_container_width=True,
      )
    else:
      st.markdown(message["content"])

# --- USER INPUT ---
if prompt := st.chat_input(
    "Discutez avec De Paul IA, analysez ou demandez une image..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    if uploaded_image_pil:
      st.image(uploaded_image_pil, width=150)
    st.markdown(prompt)

  if client:
    prompt_lower = prompt.lower()
    is_video_request = any(
        kw in prompt_lower
        for kw in [
            "video",
            "tiktok",
            "reel",
            "animated",
            "animation",
            "moving",
            "animé",
            "anime",
        ]
    )
    is_image_request = (
        uploaded_image_pil is not None
        or any(
            kw in prompt_lower
            for kw in [
                "image",
                "drawing",
                "create",
                "generate",
                "photo",
                "edit",
                "modify",
                "change",
                "dessin",
                "créer",
                "generer",
                "modifier",
                "changer",
                "afro",
            ]
        )
    )

    with st.chat_message("assistant"):
      response_success = False
      attempts = 0
      max_attempts = len(API_KEYS)

      while not response_success and attempts < max_attempts:
        try:
          if attempts > 0:
            st.session_state.api_key_index += 1
            client, _ = get_rotating_client()

          if is_video_request:
            with st.spinner(
                "🎬 De Paul IA prépare votre animation dynamique (Modèle 3.6)..."
            ):
              enhancement_response = client.models.generate_content(
                  model="gemini-3.6-flash",
                  contents=(
                      "Create an engaging, cinematic, vertical 9:16 moving"
                      f" visual animation concept based on this user request:"
                      f" '{prompt}'. Return ONLY the final English description"
                      " prompt text."
                  ),
              )
              clean_prompt = enhancement_response.text.strip()
              encoded_prompt = clean_prompt.replace(" ", "%20")
              animation_url = f"https://pollinations.ai/p/{encoded_prompt}?width=540&height=960&model=flux&seed=42&nologo=true"

              st.image(
                  animation_url,
                  caption=prompt,
                  use_container_width=True,
              )
              st.session_state.messages.append({
                  "role": "assistant",
                  "type": "animation",
                  "content": animation_url,
                  "caption": prompt,
              })
              response_success = True

          elif is_image_request:
            with st.spinner(
                "📸 De Paul IA traite et modifie votre image (Modèle 3.6)..."
            ):
              if uploaded_image_pil:
                analysis_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        uploaded_image_pil,
                        (
                            "Analyze this image and the user's editing"
                            f" instruction: '{prompt}'. Generate a detailed"
                            " professional image generation prompt in English"
                            " describing the modified version of this image."
                            " Return ONLY the prompt text."
                        ),
                    ],
                )
                clean_prompt = analysis_response.text.strip()
              else:
                enhancement_response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=(
                        "Create an ultra-realistic, hyper-detailed image prompt"
                        f" based on this user request: '{prompt}'. Return ONLY"
                        " the final English prompt text."
                    ),
                )
                clean_prompt = enhancement_response.text.strip()

              encoded_prompt = clean_prompt.replace(" ", "%20")
              image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&private=true&model=flux"

              # Application du filigrane "boblin-ai" en bas à gauche
              final_img_display = add_watermark(image_url, "boblin-ai")

              if uploaded_image_pil:
                st.image(
                    uploaded_image_pil, width=150, caption="Photo originale"
                )
              st.image(final_img_display, caption=prompt)

              st.session_state.messages.append({
                  "role": "assistant",
                  "type": "image",
                  "content": final_img_display,
                  "caption": prompt,
                  "input_image": (
                      uploaded_image_pil if uploaded_image_pil else None
                  ),
              })
              response_success = True
          else:
            with st.spinner("De Paul IA réfléchit (Modèle 3.6)..."):
              system_instruction = (
                  "You are De Paul IA, an expert, friendly, and collaborative"
                  " virtual assistant using Gemini 3.6. Structure your"
                  " responses cleanly. Respond in French."
              )

              conversation_history = ""
              for msg in st.session_state.messages[-6:]:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                if "content" in msg and isinstance(msg["content"], str):
                  conversation_history += f"{role_label}: {msg['content']}\n"

              full_context = (
                  f"{system_instruction}\n\nDiscussion"
                  f" history:\n{conversation_history}\nNew question: {prompt}"
              )

              response = client.models.generate_content(
                  model="gemini-3.6-flash", contents=full_context
              )
              reply = response.text
              st.markdown(reply)

              st.session_state.messages.append(
                  {"role": "assistant", "content": reply}
              )
              response_success = True

        except Exception as e:
          attempts += 1
          if attempts >= max_attempts:
            st.error(
                "❌ **Quota épuisé sur toutes vos clés API !** Toutes vos"
                f" {len(API_KEYS)} clés ont atteint leur limite journalière."
                " Veuillez ajouter de nouvelles clés (`GEMINI_API_KEY3`, etc.)"
                " dans vos secrets Streamlit pour continuer."
            )
  else:
    st.error("⚠️ Client non initialisé. Vérifiez vos secrets.")
