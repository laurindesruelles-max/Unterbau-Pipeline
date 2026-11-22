# Prüfbericht – 003-supermarkt-leer (2026-11-19)

## 1. Technik (automatisch, engine/qa.py)
- [x] OK: Länge 9:52 (Minimum 8:00)
- [x] OK: Bild 1920x1080
- [x] OK: Tonspur vorhanden
- [x] OK: Lautheit -14.0 LUFS (Ziel -14 ±2,5)
- [x] OK: Spitzenpegel -1.4 dBFS (max. −0,5)
- [x] OK: Schwarzbilder mitten im Video: keine
- [x] OK: Standbild-Stellen (≥4 s ohne Bewegung): 0 
- [x] OK: Dateigröße 2263 MB (Info – Upload-Kopie muss < 299 MB sein)
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

## Ergebnis der Endkontrolle (19.11.2026)
- Kontaktbogen (qa_frames.jpg, 19 Frames) angesehen: keine Tippfehler, kein abgeschnittener Text, keine Gesichter, keine Logos.
- Länge 9:52 (ffprobe 592,7 s) ≥ 8:00 ✔. Upload-Kopie 274,8 MB (< 299 MB), −14 LUFS, Spitze −1,4 dBTP.
- Spracherkennung am fertigen Ton: 94,8 % Wortübereinstimmung (Abweichungen = Zahlen als Ziffern); Anfang jedes Teils vollständig. Gefunden: „Deutschland hält Erdöl“ verschluckt → Satz neu eingesprochen („Deutschland lagert Erdöl …“).
- Ton-Check (sk.py check): Exit 0, qa_sound/sound_check.md + sheet.png angesehen. audiokit-Endkontrolle: alle Punkte OK.
- Hook-Prüfung: Thema klar bei 0–4 s („Dein Supermarkt hat fast kein Lager … kommt per Lkw nach“), offene Frage bei 10 s, Versprechen bei 25 s („Tag für Tag … bis selbst der Staat ein Problem hat“), Hook bis Titelkarte 36 s (≤ 45 s).
- Faktencheck (separater Agent, Primärquellen selbst geöffnet): alles korrekt oder gering ungenau; 1 Punkt mittel (Spanien: Abgabegrenzen) → Satz neu eingesprochen („Milch, Eier und Mehl werden knapp. Supermärkte dürfen die Abgabe begrenzen.“). Mehl-Beleg auf Destatis PE20_130 korrigiert.
- Recht: keine Namen von Privatpersonen; Gräfenhausen nur als „Vorwurf“ ohne Firmennamen; Handelsgruppen nur mit Kartellamts-Zahl, ohne Bezug zu Gräfenhausen; „Gedankenexperiment“ und „Szene nachgestellt“ im Ton und als Einblendung; KI-Hinweis in der Beschreibung, bei YouTube „Veränderte oder synthetische Inhalte“ setzen; keine fremden Fotos/Videos/Musik; keine Schwachstellen von Infrastruktur (Lagerorte nicht genannt). Keine Werbung.

## Fassung 2 (22.11.2026): Modellstadt, neues Skript, Julian Turbo
- Bild-Drehbuch: 213 Einstellungen, 22,6 Bild-Ereignisse/Min, Prüfung OK (bilddrehbuch.json, engine/bilddrehbuch.py)
- Länge 9:25, Endmix −14,3 LUFS, True Peak −2,6 dB
- earshot gegen doku_profil.json: launch-grade, 22/23, 0 major (qa_sound_v2.txt); Gemini (3.5-flash-lite) Vorschau 2 Min: 8/10, keine Fundstelle im Video
- Sound-Casting (Gemini, 22.11.): Treffer sub_drop PREMIUM, Whoosh whoosh_slow_soft PREMIUM, Uhr tick PREMIUM, Stromausfall hum_fall PREMIUM; door_open CHEAP → fridge_door_open (Freesound CC0), Rolltor Garuda1982 (CC BY, in der Beschreibung genannt)
- ASR Endmix gegen Skript: 95,1 %
- Faktencheck Skript v2: unabhängiger Agent, 20 Punkte korrigiert (siehe Verlauf)
- Shorts: 5 Ausschnitte (shorts_003.py), ohne neue Sätze
- vidIQ-Entwurf neu: postId 9ec00502-5e27-46ee-a500-b654616ad663 (geplant 24.11.2026 19:00, erst nach Laurins „ja“)
