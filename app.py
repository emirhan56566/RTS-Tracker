import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Text-Scanner")
st.write("Fotografieren Sie einen Artikel oder wählen Sie ein Bild aus Ihrer Galerie.")

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
        
        with st.spinner("Analysiere Bildmerkmale..."):
            
            # Die KI liefert nur noch saubere Textnamen zum Kopieren
            system_instruction = """Du bist ein Experte für das Sortiment von Flaschenland.de.
Deine Aufgabe ist es, das fotografierte Produkt exakt zu analysieren und dem Nutzer die 3 passendsten Artikelbezeichnungen aus dem Shop als reinen Text auszugeben.

Gib die Antwort für die Top 3 Treffer exakt in diesem Format aus (Verwende keine Sternchen oder fette Schrift im Rohtext):
Artikelbezeichnung: [Exakter Name des Artikels aus dem Shop]
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
                        contents=[image, "Ermittle die 3 passendsten Artikelbezeichnungen für dieses Produkt."],
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction
                        ),
                    )
                    
                    st.success("Analyse abgeschlossen!")
                    st.markdown("### 📋 Vorgeschlagene Artikelbezeichnungen:")
                    
                    # Zeigt die Ergebnisse als reinen, leicht markierbaren Text an
                    st.text_area("Ergebnisse (hier gedrückt halten zum Kopieren):", value=response.text, height=250)
                    
                    # --- IHRE GEWÜNSCHTE ANLEITUNG & LINK ---
                    st.write("---")
                    st.markdown("#### 🛠️ So suchen Sie den Artikel im Shop:")
                    st.markdown("-> auf vorgeschlagene Artikelbezeichnung lange gedrückt halten und somit markieren")
                    st.markdown("-> dann auf kopieren klicken")
                    st.markdown("-> auf [Flaschenland.de](https://flaschenland.de) link klicken")
                    st.markdown("-> lange gedrückthalten auf flaschenland.de Suchmaschine auf einsetzen/einfügen klicken und nach passenden Artikel suchen.")
                    
                    erfolgreich = True
                    break
                    
                except Exception as e:
                    letzter_fehler = str(e)
                    continue
            
            if not erfolgreich:
                st.error(f"Fehler: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
