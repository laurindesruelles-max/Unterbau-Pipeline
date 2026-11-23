# Prüfbericht – 004-notruf-112 (2026-11-23)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 10:24 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.2 LUFS (Ziel -14 ±2,5)
- [x] OK: Spitzenpegel -2.7 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 0 
- [x] OK: Dateigröße 881 MB (Info – Upload-Kopie muss < 299 MB sein)
- [ ] Kontaktbogen `qa_frames.jpg` angesehen: Tippfehler in Einblendungen, abgeschnittener Text, Bildfehler, Ton synchron (Stichproben)

## 2. Fakten (unabhängiger Faktencheck durch separaten Agenten)
Tabelle: Aussage im Skript | Quelle (Link) | Stimmt? (ja / teilweise / nein / unbelegt) | Korrektur
- [ ] Jede Zahl, jedes Datum, jeder Name, jedes Zitat geprüft; alles mit „nein“/„unbelegt“ wurde geändert oder gestrichen

## 3. Recht (keine Rechtsberatung – Sorgfaltsprüfung)
- [ ] Äußerungsrecht: Tatsachen nur mit Beleg; Vorwürfe/laufende Verfahren als „Vorwurf“/„laut …“; Urteile korrekt (Gericht, Jahr); Meinung als Meinung erkennbar; keine Beleidigung, keine Spekulation über Privates
- [ ] Personen: keine echten Fotos, keine realistischen KI-Gesichter realer Personen, keine Privatpersonen identifizierbar
- [ ] Marken: keine Logos/Markenzeichen im Bild oder Thumbnail; Markennamen nur beschreibend; Hinweis „not affiliated/endorsed“ in der Beschreibung
- [ ] Titel und Thumbnail versprechen nichts, was das Video nicht belegt (kein irreführender Vorwurf)

## 4. Lizenzen (Protokoll)
| Material | Quelle | Lizenz |
|---|---|---|
| Sprecherstimme | Higgsfield (Preset-Stimme) | Higgsfield-Abo (kommerzielle Nutzung laut Plan) |
| KI-Bilder / Thumbnail | Higgsfield gpt_image | Higgsfield-Abo |
| Musik | assets/music (ElevenLabs über Higgsfield) | Higgsfield-Abo |
| Geräusche | assets/sfx (SOUNDS.md) – SFXMint | CC0 |
| Geräusche | assets/sfx (SOUNDS.md) – Unterbau-eigene Effekte (CC0 / Higgsfield mirelo) | Herkunft je Sound in SOUNDS.md |
| 3D-Texturen/Modelle | Poly Haven | CC0 |
| Schriften | Anton, Special Elite, Playfair Display, Inter | SIL OFL / Apache |
- [ ] Kein fremdes Material (Filmausschnitte, Fotos, Musik) außer den oben gelisteten Quellen

## 5. YouTube
- [ ] Realistisch wirkende KI-Bilder echter Orte/Ereignisse → beim Upload „Veränderte oder synthetische Inhalte: Ja“ setzen (Laurin im Studio, falls die API es nicht kann)
- [ ] Beschreibung: Quellenliste, Kapitel, Marken-Hinweis; keine < oder > Zeichen
- [ ] Werbefreundlich: keine Gewaltbilder, keine Schimpfwörter, keine reißerischen Schock-Thumbnails mit Verletzungen

## Ergebnis: TECHNIK OK · Fakten/Recht/Lizenzen: oben abhaken, erst dann Laurin zur Freigabe schicken

## Ergebnis der Endkontrolle (23.11.2026)
- Länge 10:24 (ffprobe 624,3 s) ≥ 8:00 ✔. Lautheit −14,2 LUFS, True Peak −2,7 dB. Upload-Kopie < 299 MB (libx264, −14 LUFS, Spitze −1,5 dB).
- Kontaktbögen (alle 140 Blender-Bilder, 45 Motion-Grafiken, Teile 1–3) angesehen: keine Gesichter, keine Logos, keine Marken; Leitstellen-Außenansicht neu gerendert (Kamera stand im Gebäude).
- Spracherkennung am fertigen Ton: 91,8 % Wortübereinstimmung über das ganze Video; Abweichungen fast nur Zahlen als Ziffern („eins, eins, zwei“ → 112) und Zusammenschreibungen; erstes Wort jedes Teils vorhanden.
- engine/qa.py: alle Punkte OK (keine Schwarzbilder, keine Standbilder ≥ 4 s).
- engine/bildcheck.py: 7 gemeldete „Sprung-Schnitte“ gesichtet: 5 sind Wechsel Rathausuhr ↔ 2D-Grafik (verschiedene Motive, nur ähnliches Dunkelblau), 1 ist das gewollte „Licht springt an“ in der Wache, 1 war eine echte Naht im Hochwasser-Clip (Zoom setzte neu an) → behoben (Zoom läuft an der Clip-Zeit weiter, alle Clip-Einstellungen neu eingesetzt). Warnungen „dunkel“ = Nachtwelt/Abspann.
- earshot critique gegen doku_profil.json: **launch-grade, 21/23, 0 critical**, 1 major (0,26 s Stille am Ende) → Ende um 0,3 s gekürzt.
- Gemini (gemini-3.5-flash) hört die ersten 2 Minuten: 8/10; Hinweise umgesetzt: Kapitel-Treffer leiser (0,5 → 0,38), Zähler-Ticks leiser, Ducking langsamer (kein Pumpen).
- Sound-Casting (Gemini, 23.11.): Freizeichen dialing_tone_europe PREMIUM (phone_ring CHEAP), Martinshorn german_ambulance_passes_by PREMIUM (german_ambulance_2 CHEAP), Rolltor Garuda1982 PREMIUM, Text-Einblendung whoosh_slow_soft PREMIUM (digital_denied CHEAP, notification_failure_low OK).
- Faktencheck 1 (vor dem Einsprechen): 1 Fehler (BW-Gericht) + 10 Präzisierungen eingearbeitet (faktencheck.md).
- Faktencheck 2 (fertiges Bild, separater Agent, faktencheck_final.md): Zahlen/Daten korrekt; Grafik-Fehler behoben (Leitstellen-Punkte nur in Deutschland, Raster „jeder Zehnte“ 45 dunkel/5 hell, eCall „> 90 %“ 9 von 10, 11.11.2021 als „70 MIN“), Texte präzisiert („Bonn“ gestrichen, „110 + 112“, „Beschluss: 112 für alle 12 Länder“, „soll vernetzt werden“, „Szene 04:12 · Ausfall 04:30“, „alle Feuerwehr-Leitstellen“, „Register 2025“), Quellenliste ergänzt.
- Recht: nachgestellte Szene im Ton („Diese Szene ist nachgestellt“) und als Einblendung (Anfang und Schluss); keine Namen Verurteilter; Björn Steiger und seine Eltern nur mit der öffentlichen Stiftungsgeschichte; keine Schwachstellen von Infrastruktur (Ausfallursachen nur allgemein, wie in den Quellen); Vorwürfe vorsichtig („mit dem Ausfall in Verbindung gebracht“); keine Logos (Rotkreuz-Emblem bewusst nicht gezeigt, Rettungswagen ohne Beschriftung); KI-Hinweis in der Beschreibung, YouTube „Veränderte oder synthetische Inhalte“ = Ja.

## Lizenzen (dieses Video)
| Material | Quelle | Lizenz |
|---|---|---|
| Modellstadt, Leitstelle, Wache, Küche, Straße 1969 | eigene Blender-Szenen (engine/stadt.py, stadt_notruf.py) | eigen |
| 2D-Grafiken | engine/motion2d (Remotion), Karten world-atlas (Natural Earth, gemeinfrei) | eigen / Public Domain |
| Stimme | ElevenLabs v4 Turbo über Higgsfield | Higgsfield-Abo |
| Thumbnails | Higgsfield gpt_image_2_6 | Higgsfield-Abo |
| Echte Clips | Pixabay 129409, 1110, 204018, 86507, 7315, 87884, 4360, 14900, 14324, 4101, 63970 | Pixabay Content License |
| Geräusche | Freesound dialing_tone_europe, german_ambulance_passes_by (CC0); open close window roller shutters – Garuda1982 (CC BY, in der Beschreibung genannt); sound-bibliothek/assets/sfx | CC0 / CC BY |
| Musik | assets/music (Unterbau-Bibliothek) | Higgsfield-Abo |
