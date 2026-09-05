import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import urllib.parse

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Live-Such-Scanner")
st.write("Fotografieren Sie ein Produkt, um es sofort im Flaschenland-Shop zu suchen.")

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
        st.image(image, caption="Aufgenommenes Bild", use_container_width=True)
        
        with st.spinner("Identifiziere Artikelmerkmale für die Shop-Suche..."):
            
            # Wir zwingen die KI, sich voll auf präzise Suchbegriffe zu konzentrieren
            system_instruction = """Du bist ein Experte für das Sortiment von Flaschenland.de.
Deine einzige Aufgabe ist es, das fotografierte Produkt (Flasche, Glas oder Verschluss) zu analysieren und den exakten, spezifischen Handelsnamen oder Suchbegriff zu ermitteln, mit dem man dieses Produkt im Onlineshop findet.

Gib die Top 3 wahrscheinlichsten Artikel exakt in diesem Zeilen-Format aus (Verwende kein Markdown oder Sternchen im Rohtext):
Name: [Exakter Produktname, z.B. Glasflasche Gerardino Mündung Kork oder Marasca Ölflasche]
Grund: [Kurzer Satz, warum es dieses Produkt sein könnte]
---"""

            # Die bewährte 10-Stufen-Ausfallsicherung
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
                        contents=[image, "Ermittle die präzisesten Suchbegriffe für dieses Produkt."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success(f"Produktmerkmale erfolgreich erkannt!")
                    st.markdown("### 🔍 Klicken Sie auf einen Treffer, um ihn im Shop zu öffnen:")
                    
                    # Zerlege die Antwort in einzelne Artikel
                    artikel_bloecke = response.text.split("---")
                    for block in artikel_bloecke:
                        if "Name:" in block:
                            lines = block.strip().split("\n")
                            name, grund = "", ""
                            for line in lines:
                                if line.startswith("Name:"): 
                                    name = line.replace("Name:", "").strip()
                                elif line.startswith("Grund:"): 
                                    grund = line.replace("Grund:", "").strip()
                            
                            if name:
                                # URL-konforme Encodierung für die Onlineshop-Suche (z.B. Leerzeichen zu %20)
                                such_begriff = urllib.parse.quote(name)
                                live_shop_link = f"https://flaschenland.de{such_begriff}"
                                
                                # Anzeige als sauber formatierte Kachel auf dem iPhone
                                with st.container():
                                    st.markdown(f"#### 🔹 {name}")
                                    if grund:
                                        st.write(f"*{grund}*")
                                    # Dieser Link führt nun direkt zur echten Suchergebnis-Seite im Shop
                                    st.markdown(f"[🔍 Jetzt auf Flaschenland.de anzeigen]({live_shop_link})")
                                    st.write("---")
                                
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
