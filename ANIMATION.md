# Unterbau – Animations-Möglichkeiten (Laurin, 21.11.2026)

Ergänzt `EFFEKTE.md` (abgenommener Kern-Katalog) um alles, was zur Nische passt: unsichtbare Systeme, Infrastruktur, Lieferketten, Ausfälle und Kettenreaktionen. Markenzeichen bleibt die **Miniatur-Modellstadt bei Nacht** (Tilt-Shift gehört nur Unterbau), daneben echte Clips, Querschnitt, Karten und Grafiken – alles bewegt. Nachtblau, orange Lichter, echtes Licht statt Leuchteffekt. Für jedes Skript gilt das Bild-Drehbuch aus `HANDWERK.md`.

## Zeit und Geschehen in dieser Nische
- **Zeit:** Der **Countdown** ist das Rückgrat: „Stunde 0, Stunde 6, Tag 3“ immer exakt in der Welt (Rathausuhr, Anzeigetafel). Wer bei Unterbau nicht weiß, wie viel Zeit vergangen ist, verliert die Spannung.
- **Geschehen:** Jede Kettenreaktion **Schritt für Schritt in der richtigen Reihenfolge** zeigen (A fällt aus → B → C), jeder Schritt ein eigenes Bild-Ereignis.
- **System:** Was unter der Oberfläche passiert, wird sichtbar (Querschnitt, Leitungen, Ströme) – als Schema, aber an einem echten Ort der Stadt.
- **Neugier-Lücke:** Ein Licht flackert schon, bevor erklärt wird, warum; ein Teil der Stadt bleibt dunkel, bis das Kapitel es auflöst.

## Animations-Katalog (zusätzlich zu EFFEKTE.md)
| Animation | Was passiert | Wann | Genauigkeit | Werkzeug | Status |
| --- | --- | --- | --- | --- | --- |
| Netz-Puls | Im Querschnitt laufen orange Lichtimpulse durch Strom-, Daten- oder Wasserleitungen; bei Ausfall stocken sie | wie ein System funktioniert | schema | Blender (Emission an echten Leitungen) | bauen |
| Fluss in Rohren | Wasser/Gas fließt sichtbar durch Rohre unter der Stadt, Druck fällt ab | Wasser, Gas, Fernwärme | schema | Blender Fluid/Partikel | bauen |
| Modellbahn-Warenstrom | Güterzüge und Container rollen durch die Modellwelt, Ladung als echte Kisten | Lieferkette, Hafen | schema | Blender | bauen (ergänzt Warenstrom) |
| Menschen reagieren | Miniaturfiguren bilden Schlangen, bleiben stehen, laufen nach Hause | Folgen für Menschen | exakt (Geschehen) | Blender Partikel-Figuren | bauen |
| Was-wäre-wenn-Teilung | Die Stadt ist geteilt: links läuft alles, rechts fällt aus – gleichzeitig | Vergleich Normal/Ausfall | schema | Blender, 2 Kameras | bauen |
| Netzwerk-Karte | Modellgelände zoomt raus, Knoten (Kraftwerke, Rechenzentren, Häfen) leuchten, Verbindungen kappen sich nacheinander | Abhängigkeiten im Land | exakt | Manim-Graph → Modellgelände | bauen |
| Tag-Nacht-Zeitraffer | Schatten wandern, Lichter gehen an/aus, Uhr springt | Zeitspanne Stunden/Tage | exakt | Blender Sonne + Uhr | steht teils (Countdown), ausbauen |
| Lagerbestand-Turm | Ein Hochregal im Modell leert sich, Tage-Zähler an der Wand | „Vorrat reicht X Tage“ | exakt | Blender | bauen (ergänzt Regale leeren sich) |
| Wetter-Ereignis | Sturm/Hitze/Hochwasser im Modell, nur wenn es die Ursache ist | Auslöser | exakt | Blender Partikel/Fluid | bauen |
| Steuerzentrale | Ein Modell-Leitstand mit Bildschirmen, auf denen echte Clips/Grafiken laufen; Alarme springen an | Leitwarte, Betreiber | exakt | Blender + stock.py | bauen (ergänzt Bildschirm in der Welt) |
| Prozent als Stadtteil | Ein Anteil der Häuser färbt sich/erlischt genau im Verhältnis (z. B. 23 %) | Anteil, Prozent | exakt | Blender | bauen |
| Rückflug zum Anfang | Kamera kehrt zum Haus aus dem Hook zurück, sein Zustand hat sich verändert | Kapitelende, Rückkehr zum Hook | – | Blender | bauen |

## Werkzeuge (alle ohne Credits, getestet 21.11.2026)
| Werkzeug | Wofür | Einrichten |
| --- | --- | --- |
| Blender (`bpy`) | echtes 3D, Physik (Rigid Body, Flüssigkeit, Stoff, Partikel), Geometry Nodes für Wachstum/Aufbau, Grease Pencil für gezeichnete Linien im Raum, Rigging für Figuren | `pip install bpy` (setup.sh) |
| 2,5D-Tiefe (`depth25d.py`, Depth Anything) | jedes Standbild in Ebenen zerlegen, Kamera fährt mit Tiefe hindurch, Ebenen bewegen sich einzeln | im Goldsmith-/Unterbau-Repo vorhanden |
| PIL + numpy + ffmpeg | eigene Motion-Grafik, Partikel, Licht, Übergänge, Compositing | vorhanden |
| Manim | exakte, animierte Diagramme, Netzwerke, Abläufe, Formeln, Zählwerke – danach im Kanal-Look eingefärbt | `apt-get install -y libpango1.0-dev libcairo2-dev && pip install manim` |
| rlottie | Lottie-Vektoranimationen (Icons, kleine Abläufe) als Vorlage, immer im Kanal-Stil nachgezeichnet | `pip install rlottie-python` |
| Pixabay, Wikimedia, Archive | echte Clips und Fotos, nur innerhalb der Kanal-Welt eingebaut (siehe HANDWERK.md) | `stock.py`, `sources.py` |
| Higgsfield | nur KI-**Bilder** (0,25 Credits), Freistellen, 3D-Modell aus Bild. **Keine KI-Videoclips** (Laurin 21.11.2026) | – |

Status in den Tabellen: **steht** = in der Engine vorhanden · **bauen** = freigegeben (Laurin 21.11.2026), beim ersten Einsatz als Baustein in die Engine aufnehmen und kurz Stilprobe an Laurin.
