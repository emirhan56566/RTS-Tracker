import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Artikel-Scanner")
st.write("Fotografieren Sie einen Artikel, um die passenden Treffer aus dem Sortiment zu finden.")

# API Key Abfrage
api_key = st.text_input("Gemini API Key eingeben", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # Kamera-Input für iPhone / Android
    img_file = st.camera_input("Artikel fotografieren")

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Aufgenommenes Foto", use_container_width=True)
        
        with st.spinner("Analysiere Sortiment von Flaschenland.de..."):
            try:
                # Ihr exakter Flaschenland-Prompt
                system_instruction = (
                    "Du bist eine smarte KI zur visuellen Artikelidentifikation für das Sortiment von Flaschenland.de. "
                    "Deine Aufgabe ist es, fotografierte Artikel zu analysieren und die passendsten Treffer aus dem Shop vorzuschlagen. "
                    "Du arbeitest als hilfreicher Assistent: Anstatt bei fehlenden Details (wie einem Maßstab) abzubrechen, "
                    "zeigst du die besten verfügbaren Optionen und Wahrscheinlichkeiten auf.\n\n"
                    "Regeln für die Analyse:\n"
                    "- Visuelle Merkmale priorisieren: Analysiere die Kategorie (Flasche, Glas, Verschluss) und nutze Form, Farbe, Material und Mündung, um das Modell bestmöglich einzugrenzen.\n"
                    "- Fehlender Maßstab: Wenn das genaue Volumen nicht direkt erkennbar ist, ist das kein Problem. Schlage einfach die gängigsten oder wahrscheinlichsten Größen der erkannten Modellserie vor.\n"
                    "- Fokus auf Flaschenland.de: Ziehe für deine Vorschläge das Sortiment, die Bezeichnungen und die Artikelnummern von Flaschenland.de heran.\n\n"
                    "Verbindliches Ausgabeformat:\n"
                    "Gib nach jeder Bildanalyse automatisch deine besten Kandidaten (z. B. die Top 3 bis Top 5) in exakt dieser Struktur untereinander aus:\n"
                    "Artikelname: [Offizieller Name des Artikels]\n"
                    "Artikelnummer: [Exakte SKU]\n"
                    "Übereinstimmung: [XX] %\n"
                    "Begründung: [Ein kurzer, pragmatischer Satz, warum das Produkt optisch passt und wo eventuell geschätzt werden musste, z. B. beim Volumen.]"
                )
                
                # Wir wechseln auf das stabilere Hauptversions-Modell gemini-3.6-flash, um Serverstaus zu meiden
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[image, "Analysiere diesen Artikel und liste die besten Kandidaten auf."],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    ),
                )
                
                # Ergebnisse anzeigen
                st.success("Analyse abgeschlossen! Mögliche Treffer:")
                st.text_area("Gefundene Artikel:", value=response.text, height=400)
                
            except Exception as e:
                st.error(f"Fehler bei der Analyse: {e}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
