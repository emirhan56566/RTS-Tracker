import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Direkt-Scanner")
st.write("Fotografieren Sie einen Artikel, um die Artikelnummer und den passenden Produktlink zu erhalten.")

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
        
        with st.spinner("Analysiere Bild und generiere exakte Produktlinks..."):
            
            # Überarbeiteter System-Prompt: KI ermittelt direkt Artikel, SKU und generiert Links
            system_instruction = """Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, fotografierte Artikel (Flaschen, Gläser, Verschlüsse) exakt zu analysieren und die passendsten Treffer aus dem Onlineshop inklusive korrekter Artikelnummer und funktionierendem Produktlink bereitzustellen.

REGELN FÜR DIE AUSGABE:
1. ARTIKELNAME: Nutze die offiziellen Bezeichnungen aus dem Flaschenland-Sortiment (z.B. 'Marasca Ölflasche', 'Bordeauxflasche', 'Sturzglas').
2. ARTIKELNUMMER: Jede Artikelnummer MUSS zwingend mit den Ziffern '1000' beginnen (z.B. 10001234). Wenn dir die genaue Endung fehlt, schätze sie basierend auf typischen Flaschenland-Strukturen ab – beginne aber NIEMALS mit einer anderen Zahl!
3. PRODUKTLINK: Generiere für jeden Artikel einen direkten Link. Nutze dafür entweder:
   - Die passende Hauptkategorie auf Flaschenland, z.B.:
     * Flaschen: https://flaschenland.de
     * Gläser: https://flaschenland.de
     * Einmachgläser: https://flaschenland.de
   - Oder generiere einen exakten, direkten Suchlink im folgenden Format:
     https://flaschenland.de[ARTIKELNAME_MASHUP] (Ersetze Leerzeichen durch ein + Zeichen, z.B. q=Marasca+Oelflasche)

Verbindliches Ausgabeformat:
Gib nach der Bildanalyse automatisch deine besten Kandidaten (Top 3 bis Top 5) in exakt dieser Struktur untereinander aus:
Artikelname: [Name des Artikels]
Artikelnummer: [SKU, die mit 1000 beginnt]
Übereinstimmung: [XX] %
Begründung: [Kurzer Satz, warum das Produkt optisch passt]
Link: [Der generierte Produkt- oder Suchlink]"""

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
                        contents=[image, "Analysiere das Produkt. Gib mir Artikelname, Artikelnummer (startend mit 1000) und den passenden Direktlink."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Analyse erfolgreich über Modell {index+1}/10 (`{modell_name}`)!")
                    st.markdown("### 📋 Gefundene Artikel aus dem Shop:")
                    
                    # Gibt den Text im Interface aus. Links werden automatisch klickbar.
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
