import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Boblin AI - Studio",
    page_icon="🤖",
    layout="centered",
)

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
    }
    p, h1, h2, h3, h4, h5, h6, span, label {
        color: #ffffff !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PUBLICITÉS ADSTERRA ---
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

# --- API KEYS & ROTATION SETUP ---
api_keys = []
for i in range(1, 10):
  key_name = f"GEMINI_API_KEY_{i}"
  if key_name in st.secrets:
    api_keys.append(st.secrets[key_name])

if not api_keys and "GEMINI_API_KEY" in st.secrets:
  api_keys.append(st.secrets["GEMINI_API_KEY"])

if "key_index" not in st.session_state:
  st.session_state.key_index = 0


def get_next_client():
  if not api_keys:
    return None
  current_key = api_keys[st.session_state.key_index]
  return genai.Client(api_key=current_key)


def rotate_key():
  if len(api_keys) > 1:
    st.session_state.key_index = (st.session_state.key_index + 1) % len(
        api_keys
    )


client = get_next_client() if api_keys else None

# Detect system/browser language
accept_language = st.context.headers.get("Accept-Language", "").lower()
is_french = "fr" in accept_language

if is_french:
  default_welcome = (
      "👋 Bonjour ! Je suis **Boblin AI**. Prêt à vous aider, analyser du texte,"
      " ou modifier et créer des images et animations. Que souhaitez-vous"
      " faire ?"
  )
  new_discussion_msg = "✨ Nouvelle discussion commencée ! Comment puis-je vous aider ?"
else:
  default_welcome = (
      "👋 Hello! I am **Boblin AI**. Ready to assist you, analyze text, or edit"
      " and create images and animations. What would you like to do?"
  )
  new_discussion_msg = "✨ New discussion started! How can I help you?"

if "messages" not in st.session_state:
  st.session_state.messages = [{
      "role": "assistant",
      "content": default_welcome,
  }]

if not client:
  error_config_msg = (
      "⚠️ Veuillez configurer au moins une clé API (`GEMINI_API_KEY_1` ou `GEMINI_API_KEY`) dans les"
      " secrets de Streamlit."
      if is_french
      else "⚠️ Please configure at least one API key (`GEMINI_API_KEY_1` or `GEMINI_API_KEY`) in"
      " Streamlit secrets."
  )
  st.error(error_config_msg)

# --- TOP NAVIGATION BAR ---
col_menu, col_title, col_new = st.columns([1, 3, 1], vertical_alignment="center")

with col_menu:
  if st.button("☰", help="Open menu"):
    st.toast("Use the Streamlit sidebar menu if hidden.", icon="ℹ️")

with col_title:
  st.markdown(
      "<div style='text-align: center; font-weight: bold; color: white; font-"
      "size: 1.1rem;'>Boblin AI</div>",
      unsafe_allow_html=True,
  )

with col_new:
  if st.button("✏️", help="New discussion"):
    st.session_state.messages = [{
        "role": "assistant",
        "content": new_discussion_msg,
    }]
    st.rerun()

st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #30363d;'>", unsafe_allow_html=True)

# --- PUBLICITÉ BANNIÈRE ADSTERRA (HAUT) ---
components.html(native_banner_code, height=120)
st.markdown("<hr style='margin: 5px 0 15px 0; border-color: #30363d;'>", unsafe_allow_html=True)

# --- DISCREET ATTACHMENT OPTION ---
expander_label = (
    "➕ Ajouter une photo ou un fichier (Optionnel)"
    if is_french
    else "➕ Add photo or file (Optional)"
)
with st.expander(expander_label, expanded=False):
  uploader_label = (
      "Choisissez une image" if is_french else "Choose an image"
  )
  uploaded_file = st.file_uploader(uploader_label, type=["png", "jpg", "jpeg"])

uploaded_image_pil = None
if uploaded_file is not None:
  uploaded_image_pil = Image.open(uploaded_file)
  caption_text = (
      "Photo prête pour modification"
      if is_french
      else "Photo ready for modification"
  )
  st.image(
      uploaded_image_pil,
      caption=caption_text,
      width=150,
  )

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    if message.get("type") == "image":
      if message.get("input_image"):
        orig_caption = (
            "Photo originale" if is_french else "Original Photo"
        )
        st.image(message["input_image"], width=150, caption=orig_caption)
      st.image(message["content"], caption=message.get("caption"))
      download_text = (
          "📥 Télécharger l'image" if is_french else "📥 Download Image"
      )
      st.markdown(
          f"[{download_text}]({message['content']})", unsafe_allow_html=True
      )
    elif message.get("type") == "animation":
      st.image(
          message["content"],
          caption=message.get("caption"),
          use_container_width=True,
      )
      download_anim_text = (
          "📥 Télécharger l'animation" if is_french else "📥 Download Animation"
      )
      st.markdown(
          f"[{download_anim_text}]({message['content']})",
          unsafe_allow_html=True,
      )
    else:
      st.markdown(message["content"])

# --- USER INPUT ---
input_placeholder = (
    "Discutez, analysez ou demandez à modifier/créer une image..."
    if is_french
    else "Chat, analyze, or ask to modify/create an image..."
)
if prompt := st.chat_input(input_placeholder):
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
            ]
        )
    )

    success = False
    attempts = 0
    max_attempts = len(api_keys) if api_keys else 1

    with st.chat_message("assistant"):
      while not success and attempts < max_attempts:
        current_client = get_next_client()
        try:
          if is_video_request:
            spinner_text = (
                "🎬 Boblin prépare votre animation dynamique..."
                if is_french
                else "🎬 Boblin is crafting your dynamic animation..."
            )
            with st.spinner(spinner_text):
              enhancement_response = current_client.models.generate_content(
                  model="gemini-3.6-flash",
                  contents=(
                      "Create an engaging, cinematic, vertical 9:16 moving"
                      " visual animation concept based on this user request: "
                      f"'{prompt}'. Return ONLY the final English description"
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
              download_anim_text = (
                  "📥 Télécharger l'animation"
                  if is_french
                  else "📥 Download Animation"
              )
              st.markdown(
                  f"[{download_anim_text}]({animation_url})",
                  unsafe_allow_html=True,
              )

              st.session_state.messages.append({
                  "role": "assistant",
                  "type": "animation",
                  "content": animation_url,
                  "caption": prompt,
              })
              success = True

          elif is_image_request:
            spinner_text = (
                "📸 Boblin traite et modifie votre image..."
                if is_french
                else "📸 Boblin is processing and modifying your image..."
            )
            with st.spinner(spinner_text):
              if uploaded_image_pil:
                analysis_response = current_client.models.generate_content(
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
                enhancement_response = current_client.models.generate_content(
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

              if uploaded_image_pil:
                orig_caption = (
                    "Photo originale" if is_french else "Original Photo"
                )
                st.image(
                    uploaded_image_pil, width=150, caption=orig_caption
                )
              st.image(image_url, caption=prompt)
              download_mod_text = (
                  "📥 Télécharger l'image modifiée"
                  if is_french
                  else "📥 Download Modified Image"
              )
              st.markdown(
                  f"[{download_mod_text}]({image_url})",
                  unsafe_allow_html=True,
              )

              st.session_state.messages.append({
                  "role": "assistant",
                  "type": "image",
                  "content": image_url,
                  "caption": prompt,
                  "input_image": (
                      uploaded_image_pil if uploaded_image_pil else None
                  ),
              })
              success = True
          else:
            spinner_text = (
                "Boblin réfléchit..." if is_french else "Boblin is thinking..."
            )
            with st.spinner(spinner_text):
              system_instruction = (
                  "You are Boblin AI, an expert, collaborative virtual"
                  " assistant with deep analytical skills, precision, and"
                  " clarity. Structure your responses cleanly. Respond in the"
                  " language used by the user."
              )

              conversation_history = ""
              for msg in st.session_state.messages[-6:]:
                role_label = (
                    "User" if msg["role"] == "user" else "Assistant"
                )
                if "content" in msg and isinstance(msg["content"], str):
                  conversation_history += (
                      f"{role_label}: {msg['content']}\n"
                  )

              full_context = (
                  f"{system_instruction}\n\nDiscussion"
                  f" history:\n{conversation_history}\nNew question: {prompt}"
              )

              response = current_client.models.generate_content(
                  model="gemini-3.6-flash", contents=full_context
              )
              reply = response.text
              st.markdown(reply)

              st.session_state.messages.append(
                  {"role": "assistant", "content": reply}
              )
              success = True

        except Exception as e:
          # On bascule sur la clé suivante peu importe l'erreur pour épuiser toutes les clés configurées
          rotate_key()
          attempts += 1
          if attempts >= max_attempts:
            error_msg = (
                f"Erreur : {e}" if is_french else f"Error: {e}"
            )
            st.error(error_msg)
            break

      if not success and attempts >= max_attempts:
        limit_msg = (
            "⏳ Limite de requêtes atteinte sur toutes vos clés API. Veuillez"
            " patienter un moment."
            if is_french
            else "⏳ Rate limit reached on all API keys. Please wait a moment."
        )
        st.error(limit_msg)
  else:
    warning_msg = (
        "Veuillez configurer votre clé API pour continuer."
        if is_french
        else "Please configure your API key to continue."
    )
    st.warning(warning_msg)

# --- SCRIPT PUBLICITAIRE (BAS) ---
st.markdown("<hr style='margin: 15px 0 5px 0; border-color: #30363d;'>", unsafe_allow_html=True)
components.html(bottom_script_code, height=50)
