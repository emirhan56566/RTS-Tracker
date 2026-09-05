import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾", layout="wide")

st.title("🍾 Flaschenland.de Live-Scanner & Recherche-Center")
st.write("Fotografieren Sie ein Produkt und recherchieren Sie direkt im eingebetteten Onlineshop darunter.")

api_key = st.text_input("Gemini API Key eingeben", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    modus = st.radio("Bildquelle auswählen:", ("📸 Kamera nutzen", "🖼️ Aus Galerie laden"))
    img_file = None
    if modus == "📸 Kamera nutzen":
        img_file = st.camera_input("Artikel fotografieren")
    else:
        img_file = st.file_uploader("Bild aus Galerie auswählen", type=["jpg", "jpeg", "png"])

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Aufgenommenes Bild", use_container_width=True)
        with st.spinner("Identifiziere Artikelmerkmale für Sie..."):
            system_instruction = """Du bist ein Experte für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, das fotografierte Produkt zu analysieren und dem Nutzer präzise Suchbegriffe für den Shop zu liefern.

Gib die Top 3 wahrscheinlichsten Artikel exakt in diesem Zeilen-Format aus (Kein Markdown, keine Sternchen):
Vorgeschlagener Suchbegriff: [Exakter Name, z.B. Glasflasche Gerardino Mündung Kork]
Grund für den Treffer: [Kurzer Satz, warum es dieses Produkt sein könnte]
---"""

            modelle = [
                "gemini-3.8-flash",       
                "gemini-3.7-flash",       
                "gemini-3.6-flash",       
                "gemini-3.1-pro-preview", 
                "gemini-3-flash-preview", 
                "gemini-3.5-flash",       
                "gemini-3.5-flash-lite",  
                "gemini-3.1-flash-lite",  
                "gemini-2.5-flash",       
                "gemini-2.5-flash-lite"   
            ]
            erfolgreich = False
            letzter_fehler = ""

            for index, modell_name in enumerate(modelle):
                try:
                    response = client.models.generate_content(
                        model=modell_name,
                        contents=[image, "Ermittle die präzisesten Suchbegriffe."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    st.success("Produktmerkmale erfolgreich erkannt!")
                    st.markdown("### 📋 Erkannte Suchbegriffe für das Shop-Fenster unten:")
                    st.write(response.text)
                    erfolgreich = True
                    break
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            if not erfolgreich:
                st.error(f"Fehler: {letzter_fehler}")
                
    st.write("---")
    st.markdown("### 🏪 Flaschenland.de Live-Recherche")
    st.info("Nutzen Sie dieses Fenster, um die oben erkannten Begriffe direkt einzugeben und Artikelnummern abzugleichen.")
    shop_url = "https://flaschenland.de"
    st.components.v1.html(
        f'<iframe src="{shop_url}" width="100%" height="800px" style="border:none; border-radius:10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);"></iframe>',
        height=820
    )
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner und das Recherche-Center zu starten.")

