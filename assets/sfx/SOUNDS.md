# Unterbau-Geräusche (assets/sfx)

**Update (Laurin 19.11.2026): Gemeinsame Sound-Bibliothek für alle Kanäle** – zusätzlich zu diesem Ordner dürfen alle Effekte aus `laurindesruelles-max/sound-bibliothek` genutzt werden, gefiltert nach dem Stilprofil des Kanals (README dort, `sk.py find … --channel <kanal>`). Musik bleibt kanal-eigen. Die Regel vom 17.11. („nur eigene Effekte“) gilt damit nicht mehr.
~~**Regel (Laurin 17.11.2026): Jeder Kanal hat seine eigenen Effekte.** Unterbau nutzt nur die Sounds in diesem Ordner, NICHT die Goldsmith-Bibliothek.~~
**Regel (Laurin 17.11.2026): Unterbau-Sounds NICHT mit Higgsfield erstellen.**
Reihenfolge bei der Suche: (1) diese Liste → (2) SFX Kit auf GitHub (github.com/wyzowl/sfx-kit, 320 Sounds, CC0, git clone --depth 1) → (3) CC0 von SFXMint (Hugging Face flreey/sfxmint-cc0-sound-effects, sonst sfxmint.com) → (4) Laurin nach einem Sound aus seiner Sammlung mit ~1000 Effekten fragen. Ergebnis hier ablegen + Zeile ergänzen. Nie per Code erzeugen, nie mit Higgsfield. Musik gehört NICHT hierher (assets/music, nur eigene Unterbau-Musik).

| Name | Herkunft | Wofür |
|---|---|---|
| ub_hit | SFX Kit CC0 cinematic-slam-big (github.com/wyzowl/sfx-kit), 17.11.2026 – ersetzt Higgsfield-Version | Titelkarte, Kapitelkarte (engine: chapter_hit) |
| ub_drop | SFX Kit CC0 bass-sub-drop-medium, 17.11.2026 – ersetzt Higgsfield-Version | Abbruch vor der Auflösung, Schwarzbild |
| underwater | Higgsfield mirelo, 17.11.2026 (alt, vor der Regel „kein Higgsfield“; ersetzen, sobald CC0-Alternative da) („deep underwater ambience, muffled low rumble …“) | Raumklang unter Wasser (amb) |
| anchor_chain | Higgsfield mirelo, 17.11.2026 (alt, vor der Regel „kein Higgsfield“; ersetzen, sobald CC0-Alternative da) („heavy ship anchor chain rattling … splash“) | Anker fällt |
| ub_klick | SFXMint CC0 carabiner-gate-click-01 (über Hugging Face) | **NICHT MEHR VERWENDEN, auch nicht als Erkennungssound** (Nachfolger für Text-Einblendungen: Casting 22.11.2026, bis dahin whoosh_slow_soft) (Laurin 19.11.2026: klingt wie Kamera-Auslöser/Ratsche) → whoosh_slow_soft |
| ub_whoosh | SFX Kit CC0 whoosh-slow-hard | Übergänge, Diagramm/Grafik kommt rein (ersetzt diagram_whoosh) |
| ub_riser | SFX Kit CC0 riser-2s-strong | Spannungsaufbau vor Zoom/Enthüllung, Höhepunkt am Ende (ersetzt zoom_riser) |
| ub_daten | SFXMint CC0 data-processing-01 (über Hugging Face) | **NICHT MEHR VERWENDEN** (Laurin 19.11.2026: „Müll“, Quietsch-/Piepton) → diagram_whoosh + reveal_impact_01 |
| whoosh_slow_soft | Sound-Bibliothek, CC0 (sk.py get whoosh_slow_soft) | Text-Einblendungen (Bauchbinde, Zahl) leise, Szenenwechsel sehr leise |
| diagram_whoosh | Sound-Bibliothek, Laurins Sammlung | Grafik/Karte kommt rein (tiefer Whoosh) |
| reveal_impact_01 | Sound-Bibliothek, CC0 | Zahl/Balken landet (tiefer Impact) |
| harbor_ships | SFXMint CC0 (über goldsmith-pipeline assets/sfx) | Meer mit Schiffshorn (amb) |
