import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Flaschenland Scanner", page_icon="🍾")

st.title("🍾 Flaschenland.de Scanner (10-Stufen-Ausfallsicherung)")
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
        
        with st.spinner("Analysiere Sortiment von Flaschenland.de..."):
            
            # System-Prompt für Flaschenland.de
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

            # Die 10 Modelle von der neuesten Spitzenklasse bis zum sichersten Ausfallschutz
            modelle = [
                "gemini-3.8-flash",       # 1. Neueste Intelligenzspitze
                "gemini-3.7-flash",       # 2. Aktuelles High-End Flash
                "gemini-3.6-flash",       # 3. Solider Standard
                "gemini-3.1-pro-preview", # 4. Tiefes Reasoning
                "gemini-3-flash-preview", # 5. Schnelles Multimodal
                "gemini-3.5-flash",       # 6. Etablierter Vorgänger
                "gemini-3.5-flash-lite",  # 7. Schnelles Lite-Modell
                "gemini-3.1-flash-lite",  # 8. Schlankes Backup
                "gemini-2.5-flash",       # 9. Hochverfügbares Legacy-Modell
                "gemini-2.5-flash-lite"   # 10. Höchste Ausfallsicherheit gegen 503
            ]
            
            erfolgreich = False
            letzter_fehler = ""

            # Automatische Kaskade
            for index, modell_name in enumerate(modelle):
                try:
                    response = client.models.generate_content(
                        model=modell_name,
                        contents=[image, "Analysiere diesen Artikel und liste die besten Kandidaten auf."],
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
                    # Springt bei 503, 404 oder Rate Limits direkt zum nächsten Modell
                    continue
            
            if not erfolgreich:
                st.error(f"Keines der 10 Modelle konnte antworten. Letzte Meldung: {letzter_fehler}")
else:
    st.info("Bitte tragen Sie oben Ihren Gemini API Key ein, um den Scanner zu starten.")
