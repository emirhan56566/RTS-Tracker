import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Direkt-Link Scanner")
st.write("Fotografieren Sie einen Artikel, um die echte Artikelnummer und den passenden Direkt-Link zu erhalten.")

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
        
        with st.spinner("Analysiere Bild und generiere Direkt-Links..."):
            
            # Überarbeiteter System-Prompt: KI baut die URL exakt nach dem neuen Muster zusammen
            system_instruction = """Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, fotografierte Artikel exakt zu analysieren und die passendsten Treffer aus dem Onlineshop inklusive korrekter Artikelnummer und dem exakten Direkt-Link bereitzustellen.

STRANGE REGELN FÜR DIE AUSGABE:
1. ARTIKELNAME: Nutze die offiziellen Bezeichnungen aus dem Flaschenland-Sortiment (z.B. 'Bordeauxflasche 750ml grün' oder 'Glasflasche Gerardino Mündung Kork').
2. ARTIKELNUMMER: Jede Artikelnummer MUSS zwingend mit den Ziffern '1000' beginnen (z.B. 100031580). Schätze die Nummer basierend auf echten Flaschenland-Strukturen ab, falls du sie nicht exakt weißt. Sie darf NIEMALS mit anderen Zahlen starten.
3. PRODUKTLINK-STRUKTUR: Baue den Link für jeden Artikel exakt nach dem folgendem URL-Muster zusammen:
   https://www.flaschenland.de/[ARTIKELNAME-MIT-BINDESTRICHEN]-[ARTIKELNUMMER]
   
   Beispiele für die Link-Generierung:
   - Artikel: Glasflasche Gerardino Mündung Kork mit Nummer 100031580 -> Link: https://www.flaschenland.de/1000-ml-glasflasche-gerardino-muendung-kork-100031580
   - Artikel: Marasca Oelflasche 250ml mit Nummer 10001105 -> Link: https://flaschenland.de

Verbindliches Ausgabeformat:
Gib nach der Bildanalyse automatisch deine besten Kandidaten (Top 3 bis Top 5) in exakt dieser Struktur untereinander aus:
Artikelname: [Name des Artikels]
Artikelnummer: [SKU, die mit 1000 beginnt]
Übereinstimmung: [XX] %
Begründung: [Kurzer Satz, warum das Produkt optisch passt]
Link: [Der nach dem Muster generierte Direkt-Link]"""

            # Die 10 ausfallsicheren Modelle als Kaskade
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
                        contents=[image, "Analysiere das Produkt. Baue den Link exakt nach der Vorgabe: Name-mit-Bindestrichen-Artikelnummer zusammen."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Analyse erfolgreich über Modell {index+1}/10 (`{modell_name}`)!")
                    st.markdown("### 📋 Gefundene Artikel aus dem Shop:")
                    
                    # Gibt den Text im Interface aus. Die Links im Format https://... werden sofort klickbar.
                    st.write(response.text)
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler bei der Analyse: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
