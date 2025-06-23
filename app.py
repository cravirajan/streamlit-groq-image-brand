# app.py

import streamlit as st
import base64
import requests
from io import BytesIO
import os

st.set_page_config(page_title="📷 Bag Brand Detector", page_icon="📷")

st.title("📷 Bag Brand Detector")
st.markdown("Upload an image of a bag, and I'll tell you the brand!")

api_key = os.getenv("GROQ_API_KEY")  # For local dev
if not api_key:
    api_key = st.secrets.get("GROQ_API_KEY")  # For Streamlit Cloud deployment

if not api_key:
    st.error("API key not found. Please set GROQ_API_KEY in environment or secrets.")
    st.stop()

def analyze_image(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is brand of the bag, give me the bag brand only as an output?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ],
        "max_tokens": 50
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions",  json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")

    return response.json()["choices"][0]["message"]["content"].strip()

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.button("Detect Brand"):
        with st.spinner("Analyzing..."):
            try:
                image_bytes = uploaded_file.read()
                result = analyze_image(image_bytes)
                st.success(f"Brand: **{result}**")
            except Exception as e:
                st.error(f"Error: {str(e)}")