# ---------------------------------------------------------
# SYSTÈME DE ROTATION DES CLÉS API (Format individuel)
# ---------------------------------------------------------
api_keys_list = []

# Récupérer GEMINI_API_KEY1 à GEMINI_API_KEY10 depuis les Secrets
for i in range(1, 15):
    key = st.secrets.get(f"GEMINI_API_KEY{i}", "")
    if key and key.strip():
        api_keys_list.append(key.strip())

# Repli : si GEMINI_API_KEYS (liste) est définie
if not api_keys_list:
    raw_keys = st.secrets.get("GEMINI_API_KEYS", "")
    if raw_keys:
        api_keys_list = [k.strip() for k in str(raw_keys).split(",") if k.strip()]

# Saisie manuelle dans la barre latérale si aucun secret n'est trouvé
if not api_keys_list:
    user_key_input = st.sidebar.text_input("Vos clés API :", type="password")
    api_keys_list = [k.strip() for k in user_key_input.split(",") if k.strip()]
