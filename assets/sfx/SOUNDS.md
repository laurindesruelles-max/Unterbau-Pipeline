# Unterbau-Geräusche (assets/sfx)

**Regel (Laurin 17.11.2026): Jeder Kanal hat seine eigenen Effekte.** Unterbau nutzt nur die Sounds in diesem Ordner, NICHT die Goldsmith-Bibliothek.
**Regel (Laurin 17.11.2026): Unterbau-Sounds NICHT mit Higgsfield erstellen.**
Reihenfolge bei der Suche: (1) diese Liste → (2) CC0 von SFXMint (Hugging Face flreey/sfxmint-cc0-sound-effects, sonst sfxmint.com) → (3) Laurin nach einem Sound aus seiner Sammlung mit ~1000 Effekten fragen. Ergebnis hier ablegen + Zeile ergänzen. Nie per Code erzeugen, nie mit Higgsfield. Musik gehört NICHT hierher (assets/music, nur eigene Unterbau-Musik).

| Name | Herkunft | Wofür |
|---|---|---|
| ub_hit | Higgsfield mirelo, 17.11.2026 („single deep cinematic impact hit …“) | Titelkarte, Kapitelkarte (engine: chapter_hit) |
| ub_drop | Higgsfield mirelo, 17.11.2026 („deep cinematic sub bass drop …“) | Abbruch vor der Auflösung, Schwarzbild |
| underwater | Higgsfield mirelo, 17.11.2026 („deep underwater ambience, muffled low rumble …“) | Raumklang unter Wasser (amb) |
| anchor_chain | Higgsfield mirelo, 17.11.2026 („heavy ship anchor chain rattling … splash“) | Anker fällt |
| ub_klick | SFXMint CC0 carabiner-gate-click-01 (über Hugging Face) | Text-Einblendungen: Bauchbinde, Zahl (engine, ersetzt text_click) |
| ub_uebergang | SFXMint CC0 transition-glitch-08 „Soft Digital Glitch Stutter“ (über Hugging Face) | Übergänge, Diagramm/Grafik kommt rein (ersetzt diagram_whoosh) |
| ub_riser | SFXMint CC0 transition-riser-01 (über Hugging Face) | Spannungsaufbau vor Zoom/Enthüllung (ersetzt zoom_riser) |
| ub_daten | SFXMint CC0 data-processing-01 (über Hugging Face) | Daten-Grafik baut sich auf, Netz-/System-Visualisierung |
| harbor_ships | SFXMint CC0 (über goldsmith-pipeline assets/sfx) | Meer mit Schiffshorn (amb) |
