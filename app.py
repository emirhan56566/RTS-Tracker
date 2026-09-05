import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Scanner (Datenbank & Shop-Abgleich)")
st.write("Fotografieren Sie einen Artikel oder wählen Sie ein Bild aus Ihrer Galerie.")

# 1. PRIO 1: IHRE LOKALE PRODUKT-DATENBANK
# Tragen Sie hier bevorzugte Artikel ein, die zuerst abgeglichen werden sollen:
PRODUKT_DATENBANK = """
[START DATENBANK]
- Artikelname: Bordeauxflasche 750ml grün | Artikelnummer: 1004123
- Artikelname: Facetten-Glaskrug 1 Liter klar | Artikelnummer: 1005221
- Artikelname: Bügelflasche 500ml antik | Artikelnummer: 1003984
- Artikelname: Marasca Ölflasche 250ml eckig | Artikelnummer: 1001105
- Artikelname: Sturzglas 230ml mit Twist-Off Mündung | Artikelnummer: 1008741
- Artikelname: Kronenkorken 26mm Gold (100er Pack) | Artikelnummer: 1002244
- Artikelname: Dorica Olivenölflasche 500ml | Artikelnummer: 1001150
[ENDE DATENBANK]
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
        
        with st.spinner("Führe zweistufige Analyse durch (1. Datenbank -> 2. Onlineshop)..."):
            
            # Zweistufiger Prompt: Erst Datenbank, dann Online-Shop
            system_instruction = f"""Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, fotografierte Artikel in zwei aufeinanderfolgenden Schritten abzugleichen:

SCHRITT 1 (Höchste Priorität - Datenbank-Abgleich):
Prüfe zuerst, ob das fotografierte Produkt exakt zu einem der Artikel aus dieser Liste passt:
{PRODUKT_DATENBANK}
Wenn ja, nutze zwingend den Namen und die Artikelnummer aus dieser Liste.

SCHRITT 2 (Sekundäre Priorität - Onlineshop-Abgleich):
Falls das Produkt NICHT in der obigen Liste existiert oder ein anderes Volumen hat, nutze dein allgemeines Wissen über das Gesamtsortiment des offiziellen Onlineshops von Flaschenland.de.
Generiere in diesem Fall den passendsten Artikelnamen und schätze die Artikelnummer ab. Jede Artikelnummer MUSS zwingend mit '100' beginnen!

Allgemeine Regeln für die Analyse:
- Visuelle Merkmale (Form, Farbe, Mündung, Verschlussart) priorisieren.
- Fehlender Maßstab: Wenn das Volumen nicht exakt erkennbar ist, schlage die wahrscheinlichsten Größen der Modellserie vor.

Verbindliches Ausgabeformat:
Gib nach der Bildanalyse automatisch deine besten Kandidaten (Top 3 bis Top 5) in exakt dieser Struktur untereinander aus:
Artikelname: [Name des Artikels]
Artikelnummer: [Exakte SKU, MUSS mit 100 beginnen]
Quelle: [Entweder 'Datenbank' oder 'Onlineshop-Abgleich']
Übereinstimmung: [XX] %
Begründung: [Warum passt dieses Produkt optisch zum Foto?]"""

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
                        contents=[image, "Analysiere dieses Bild gemäß der zweistufigen Systemanweisung."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Analyse erfolgreich über Modell {index+1}/10 (`{modell_name}`)!")
                    st.text_area("Gefundene Artikel (Prio: 1. Datenbank / 2. Shop):", value=response.text, height=450)
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
