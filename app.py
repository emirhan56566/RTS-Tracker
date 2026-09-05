import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Scanner (Mit Produkt-Datenbank)")
st.write("Fotografieren Sie einen Artikel oder wählen Sie ein Bild aus Ihrer Galerie.")

# 1. IHRE PRODUKT-DATENBANK (Flaschenland Sortiment)
# Tragen Sie hier Ihre echten Artikelnamen und Artikelnummern ein:
PRODUKT_DATENBANK = """
Hier ist die offizielle Produktliste von Flaschenland.de mit korrekten SKUs:
- Artikelname: Bordeauxflasche 750ml grün | Artikelnummer: 1004123
- Artikelname: Facetten-Glaskrug 1 Liter klar | Artikelnummer: 1005221
- Artikelname: Bügelflasche 500ml antik | Artikelnummer: 1003984
- Artikelname: Marasca Ölflasche 250ml eckig | Artikelnummer: 1001105
- Artikelname: Sturzglas 230ml mit Twist-Off Mündung | Artikelnummer: 1008741
- Artikelname: Kronenkorken 26mm Gold (100er Pack) | Artikelnummer: 1002244
- Artikelname: Dorica Olivenölflasche 500ml | Artikelnummer: 1001150
"""

# API Key Abfrage
api_key = st.text_input("Gemini API Key eingeben", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Auswahl der Bildquelle
    modus = st.radio("Bildquelle auswählen:", ("📸 Kamera nutzen", "🖼️ Aus Galerie laden"))
    
    img_file = None
    if modus == "📸 Kamera nutzen":
        img_file = st.camera_input("Artikel fotografieren")
    else:
        img_file = st.file_uploader("Bild aus Galerie auswählen", type=["jpg", "jpeg", "png"])

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Zu analysierendes Bild", use_container_width=True)
        
        with st.spinner("Gleiche Bild mit Flaschenland-Datenbank ab..."):
            
            # Der Prompt füttert die KI nun mit den ECHTEN Datenbank-Daten
            system_instruction = ff"""Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, fotografierte Artikel zu analysieren und den passendsten Treffer aus der unten bereitgestellten Produktdatenbank zuzuordnen.

{PRODUKT_DATENBANK}

Regeln für die Analyse:
- Vergleiche das Foto intensiv mit den Produkten aus der Produktliste.
- Wähle nur Artikelnummern aus, die oben in der Liste stehen und mit '100' beginnen.
- Wenn das genaue Volumen nicht erkennbar ist, wähle das wahrscheinlichste Modell aus der Liste.

Verbindliches Ausgabeformat:
Gib nach jeder Bildanalyse automatisch deine besten Kandidaten (z. B. die Top 3) in exakt dieser Struktur untereinander aus:
Artikelname: [Name aus der obigen Liste]
Artikelnummer: [Passende Artikelnummer aus der Liste]
Übereinstimmung: [XX] %
Begründung: [Warum passt dieses Produkt optisch zum Foto?]"""

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
                        contents=[image, "Finde diesen Artikel in der bereitgestellten Flaschenland-Produktliste."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Treffer über Modell {index+1}/10 (`{modell_name}`)!")
                    st.text_area("Gefundene Artikel:", value=response.text, height=400)
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
