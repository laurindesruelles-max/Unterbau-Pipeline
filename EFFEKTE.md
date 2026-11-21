# Unterbau – Handschrift und Effekte (von Laurin abgenommen am 20.11.2026)

Gemeinsame Regeln: `HANDWERK.md`. Hier steht nur, was Unterbau von den anderen Kanälen unterscheidet. Ergänzt `KANAL.md`. Bei Widerspruch gilt diese Datei, weil sie neuer ist.
Weitere freigegebene Animationsarten für die Nische und die Bild-Drehbuch-Regeln: `ANIMATION.md` (21.11.2026).

## Erkennungsmerkmale
| | Unterbau |
| --- | --- |
| Sprache | Deutsch |
| Welt | Miniatur-Modellstadt bei Nacht (`engine/miniwelt.py`) als Markenzeichen und Hauptform, aber **nicht das einzige Mittel** (Laurin, 20.11.2026). Daneben echte Clips, Querschnitt, animierte Karten und Grafiken, solange alles durchgehend bewegt ist |
| Technik | Blender-Miniaturwelt plus Querschnitt. Mischform: Einzelbilder mit Tiefeninfo plus 2,5D-Kamera und animierten Ebenen, echtes 3D für Schlüsselmomente |
| Farben | Nachtblau, orange Lichter (echtes Licht, kein Leuchteffekt) |
| Kamera | Tilt-Shift-Flug über die Stadt (gehört nur Unterbau) |
| Tempo | ~3,4 s, Countdown-Druck |
| Schrift | Inter, sachlich |
| Übergang | Flug durch die Stadt zum nächsten Ort |
| Zahlen und Karten | in der Welt: Regale, Lichter, Anzeigetafel, Countdown-Uhr, Modellgelände |
| Musik | filmisch, Countdown-Puls, Pausen vor großen Sätzen |
| Stimme | Julian (ElevenLabs v4 Turbo) |

## Effekt-Katalog (nur diese verwenden)
| Effekt | Was passiert | Wann | Status |
| --- | --- | --- | --- |
| Dein Haus | Ein Haus in der Stadt ist „deins“, mit Licht im Fenster | wenn der Du-Bezug trägt, **kein Pflicht-Start** (Laurin, 20.11.2026) | neu, Stilprobe 20.11. |
| Countdown in der Welt | Die Uhr am Rathaus springt weiter, Tag und Nacht wechseln | Spannungslinie | neu |
| Lichter gehen aus | Straße für Straße erlöschen die Fenster | Ausfall, Kettenreaktion | neu, Stilprobe 20.11. |
| Warenstrom | Orange LKW-Lichter fahren über die Straßen und werden weniger | Lieferketten | neu |
| Regale leeren sich | Im Modell-Supermarkt verschwinden die Waren Reihe für Reihe | Mangel | neu |
| Querschnitt | Die Oberfläche reißt auf und zeigt das System darunter | Einstieg und Schluss | steht (`xsection`) |
| Tilt-Shift-Flug | Die Kamera fliegt zum nächsten Ort | Übergang | steht |
| Modell-Karte | Die Stadt zoomt raus zur Landkarte als Modellgelände | größerer Maßstab | neu, ersetzt die flache Karte |
| Zahl in der Welt | Die Zahl klappt auf einer Anzeigetafel am Bahnhof um | harte Zahl | neu, ersetzt den flachen Zähler |
| Balken als Häuser | Die Werte wachsen als Häuserzeilen | Vergleich | neu, ersetzt flache Balken |
| Leben in der Welt | fahrende Autos, Rauch, Lichter; Regen oder Nebel **nur wenn die Geschichte es verlangt** (Laurin 20.11.2026) | durchgehend | steht (2,5D-fx) |
| Bildschirm in der Welt | Echte Clips (Pixabay) laufen auf einem Fernseher oder Plakat im Modell | echte Bilder | neu |
| Ablauf-Kette | Ein Teil des Systems fällt nach dem anderen wie Dominosteine | „Wenn A ausfällt, dann …“ | neu |

**Raus:** KI-Standbilder mit Kamerafahrt als eigene Einstellung. Sie kommen nur noch als Bildschirm in der Welt vor.

Stilprobe: `stilprobe_unterbau.mp4` (20.11.2026, Test der Mischform). Sounds folgen nach dem Casting (`doku-ohren`).

## Sound je Effekt (Stand 20.11.2026, Version 2 von Laurin abgenommen: „Besser!“)
Geplant nach dem Grundsatz aus `HANDWERK.md`: erst festlegen, wo überhaupt ein Sound hingehört, dann je Stelle genau einen. Skripte: `engine/stilproben/ton_*.py`.

| Effekt | Sound |
| --- | --- |
| Countdown in der Welt | paper_flip (Fallblatt) pro Sprung, bei der vollen Stunde Musik-Abbruch + weicher sub_drop (kein harter Anschlag) |
| Lichter gehen aus | **keine Einzel-Klacks** (Laurin 20.11.: door_lock_01 klang wie Schüsse, nie verwenden). Stadtbrummen fällt in der Tonhöhe ab und erstirbt (`hum_stromausfall`, aus fire_electric_hum_39 per Tonhöhen-Gleiten, siehe ton_unterbau.py) |
| Dein Haus | whoosh_slow_soft leise; Licht aus: nur leiser ub_drop |
| Wetter | amb_rain leise, nur wenn es im Bild regnet, und Regen ist kein Standard |
| Musik | ub_system_puls bis zum Abbruch, danach ub_ausfall_dunkel |
