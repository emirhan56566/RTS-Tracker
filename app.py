import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import json

st.title("📦 Produkt-Scanner")
st.write("Mach ein Foto, um Artikelname und Nummer zu erkennen.")

# API Key sicher laden oder über das UI abfragen
api_key = st.text_input("Gemini API Key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Kamera-Input (aktiviert die Handykamera)
    img_file = st.camera_input("Foto aufnehmen")

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Aufgenommenes Foto", use_container_width=True)
        
        with st.spinner("Analysiere Bild..."):
            try:
                system_instruction = (
                    "Du bist ein präziser Produkt-Scanner. Analysiere das Bild und gib "
                    "Artikelname und Artikelnummer im reinen JSON-Format zurück. "
                    "Struktur: {\"artikelname\": \"...\", \"artikel_nr\": \"...\"}"
                )
                
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[image, "Extrahiere Artikelname und Artikelnummer."],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json"
                    ),
                )
                
                # Ergebnis anzeigen
                daten = json.loads(response.text)
                st.success("Ergebnis gefunden!")
                st.metric(label="Artikelname", value=daten.get("artikelname", "Nicht gefunden"))
                st.metric(label="Artikelnummer", value=daten.get("artikel_nr", "Nicht gefunden"))
                
            except Exception as e:
                st.error(f"Fehler: {e}")
else:
    st.info("Bitte gib oben deinen Gemini API Key ein.")
