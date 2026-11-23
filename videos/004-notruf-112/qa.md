# Prüfbericht – 004-notruf-112 (2026-11-23)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 10:24 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.2 LUFS (Ziel -14.0 ±2,5)
- [x] OK: Spitzenpegel -2.8 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 0 
- [x] OK: Dateigröße 1193 MB (Info – Upload-Kopie muss < 299 MB sein)
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
