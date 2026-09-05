import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import re

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Direkt-Link Scanner")
st.write("Fotografieren Sie einen Artikel, um die echte Artikelnummer und den passenden Direkt-Link zu erhalten.")

# Hilfsfunktion zur Bereinigung der URLs auf dem iPhone
def bereinige_url_text(text):
    text = text.lower()
    # Umlaute korrekt ersetzen
    text = text.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    # Sonderzeichen wie Anführungszeichen entfernen, Leerzeichen zu Bindestrichen machen
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

# API Key Abfrage
api_key = st.text_input("Gemini API Key eingeben", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Auswahl der Bildquelle (Kamera oder Galerie)
    modus = st.radio("Bildquelle auswählen:", ("📸 Kamera nutzen", "🖼️ Aus Galerie laden"))
    
    img_file = None
    if modus == "📸 Kamera nutzen":
        img_file = st.camera_input("Artikel fotografieren")
    else:
        img_file = st.file_uploader("Bild aus Galerie auswählen", type=["jpg", "jpeg", "png"])

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Zu analysierendes Bild", use_container_width=True)
        
        with st.spinner("Analysiere Bild und generiere fehlerfreie Direkt-Links..."):
            
            # Der Prompt liefert strukturierte Rohdaten an Python
            system_instruction = """Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, fotografierte Artikel exakt zu analysieren und Rohdaten bereitzustellen.

REGELN FÜR DIE AUSGABE:
1. ARTIKELNAME: Nutze die offiziellen Bezeichnungen aus dem Flaschenland-Sortiment (z.B. '1000 ml Glasflasche Gerardino Mündung Kork').
2. ARTIKELNUMMER: Jede Artikelnummer MUSS zwingend mit den Ziffern '1000' beginnen (z.B. 100031580). 

Gib die Antwort für die Top 3 Treffer exakt in diesem Zeilen-Format aus, verwende KEIN Markdown oder fette Schrift im Rohtext:
Name: [Name des Artikels]
Nummer: [SKU startend mit 1000]
Prozent: [XX]
Grund: [Kurzer Satz zur Begründung]
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
                        contents=[image, "Analysiere das Bild und liefere die strukturierten Rohdaten."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Analyse erfolgreich über Modell {index+1}/10 (`{modell_name}`)!")
                    st.markdown("### 📋 Gefundene Artikel aus dem Shop:")
                    
                    # Verarbeitung des KI-Textes in eine klickbare UI
                    artikel_bloecke = response.text.split("---")
                    for block in artikel_bloecke:
                        if "Name:" in block and "Nummer:" in block:
                            lines = block.strip().split("\n")
                            name, nummer, prozent, grund = "", "", "", ""
                            for line in lines:
                                if line.startswith("Name:"): name = line.replace("Name:", "").strip()
                                elif line.startswith("Nummer:"): nummer = line.replace("Nummer:", "").strip()
                                elif line.startswith("Prozent:"): prozent = line.replace("Prozent:", "").strip()
                                elif line.startswith("Grund:"): grund = line.replace("Grund:", "").strip()
                            
                            if name and nummer:
                                # Erstellung der fehlerfreien URL ohne Umlaute
                                bereinigter_name = bereinige_url_text(name)
                                direkt_link = f"https://www.flaschenland.de/{bereinigter_name}-{nummer}"
                                
                                # Schöne Darstellung auf dem iPhone-Bildschirm
                                st.markdown(f"**🔹 {name}** ({prozent}%)")
                                st.write(f"**Artikelnummer:** {nummer}")
                                st.write(f"**Begründung:** {grund}")
                                st.markdown(f"[➡️ Direkt zum Produkt auf Flaschenland.de]({direkt_link})")
                                st.write("---")
                                
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler bei der Analyse: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
