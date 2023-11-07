set > .env

# base64 -i config.json
echo ${CONFIG_JSON_BASE64} | base64 --decode > config.json

mkdir .streamlit
echo ${STREAMLIT_SECRETS_BASE64} | base64 --decode > .streamlit/secrets.toml