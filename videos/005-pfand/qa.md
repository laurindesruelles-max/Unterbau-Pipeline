# Prüfbericht – 005-pfand (26.11.2026)

## 1. Technik (engine/qa.py, ffprobe)
- [x] Länge **11:03,96** (Minimum 8:00; Ziel 8:30–10:30 leicht überschritten, Sprechzeit 10:32)
- [x] 1920x1080, Tonspur, −14,0 LUFS, Spitze −1,9 dBFS (Upload-Kopie: −14 LUFS)
- [x] keine Schwarzbilder, keine Standbilder ≥ 4 s
- [x] Kontaktbogen `qa_frames.jpg` angesehen (Einblendungen lesbar, nichts abgeschnitten)
- [x] Bild-Drehbuch-Prüfung (`engine/bilddrehbuch.py`): 0 Fehler, 200 Einstellungen, 18,1 Bild-Ereignisse/Min
- [x] `engine/bildcheck.py`: 3 Meldungen „Sprung-Schnitt“ bei 323,6 s, 325,6 s und 525,6 s – geprüft: **Fehlalarme**. Dort erscheint bzw. verschwindet nur eine Einblendung über einem ruhigen Drohnen-Clip bzw. der Rathausuhr; es gibt keinen Schnitt (Frames angesehen). Vorher echte Fehler bei 323,6 s und 571,4 s (Stadt→Deponie, Dokument→Kassendisplay) durch andere Schauplätze behoben.
- [x] Spracherkennung am fertigen Ton (Parakeet): Übereinstimmung 93,9 % mit dem Skript; Abweichungen sind Erkennungsfehler an Wortenden („glei“, „Abrechnirmen“), Stichproben gehört über Gemini: Stimme klar.

## 2. Ton (Skill doku-ohren)
- Sound-Casting Gemini (gemini-3-flash-preview): Piep `retail_scanner_1` PREMIUM (money_card_tap CHEAP, digital_denied OK), Text-Einblendung `whoosh_slow_soft` PREMIUM (digital_denied CHEAP), Flaschen zerdrücken `crushing_plastic_bottles` (Freesound CC0, OleSouWester) PREMIUM, Geldzähler `banknote_counter` PREMIUM, Fabrik-Atmo `amb_factory` PREMIUM; Münze, Glasklirren, Zug nur OK → nicht verwendet.
- earshot critique (Profil fern/Simplicissimus/Our Planet): 1. Mix „close“ 20/23 (1 major: 0,5 s Stille am Ende) → Ende gekürzt, Mitten +2,5 dB bei 2,2 kHz, Sub +3,5 dB bei 45 Hz → **launch-grade 23/23, 0 major** (siehe unten Endfassung).
- Gemini hört die ersten 2 Minuten: 7,5/10; Fundstellen: Automat/Band zu leer, Presse dünn → Maschinen-Atmo unter Automat, Band und Zählzentrum, Sub-Drop unter der Presse ergänzt.
- 64 Whooshes in 11 Min. (≈ 5,8/Min, Regel ≈ 4–5), Musik ≥ 16 dB unter der Stimme (ton_005.py, Decke wie 004).

## 3. Fakten
- Kritiker-Agent (Skript-Bibel): 30 Änderungen, u. a. Auflösung ins letzte Drittel (Kap. 5), kein Markenname beim Pfandschlupf.
- Faktencheck Sprechtext (faktencheck.md): 2 Fehler + 18 Präzisierungen eingearbeitet (u. a. „sieben zugelassene Firmen“, Grenzhandel nie legal, Materialart, Stand Gerichtsverfahren).
- Faktencheck Bildschirm-Texte (einblendungen.txt, separater Agent): 12 Präzisierungen eingearbeitet (Planke-Automat statt „erster Pfandautomat“, Quellen an Balken, Pfand-PET, „Stand Mai 2026“, „sinngemäß“, „rechnerisch“, Pin Dänemark, EU statt Europa). Zitate BT-Drs. 21/3361 und § 46 VerpackDG live wörtlich geprüft.
- Vor Upload erneut prüfen: Stand VG Schleswig 6 A 74/21 (im Video: „war damals noch nicht rechtskräftig“).

## 4. Recht (keine Rechtsberatung – Sorgfaltsprüfung)
- [x] Keine Namen Beschuldigter/Verurteilter; Neuss = rechtskräftiger Freispruch, Berlin = Verdacht/Razzia ohne bekanntes Urteil, 2016 = Ausgang unbekannt.
- [x] Marken nur beschreibend; Discounter beim Pfandschlupf anonym („ein großer Discounter“), Hinweis „keine Verbindung“ in der Beschreibung.
- [x] Keine Logos im Bild (Pfandzeichen nur als Wort, Fahnen DE/DK sind Hoheitszeichen ohne Logo), keine Gesichter (Modellfiguren).
- [x] Szene nachgestellt (Ton + Einblendung, Anfang und Schluss).
- [x] KI-Kennzeichnung: Beschreibung + beim Upload „Veränderte oder synthetische Inhalte: Ja“.
- [x] Keine Anleitung zum Betrug: Manipulation nur allgemein („zerdrückt die Flasche nicht“), wie in der Presse.

## 5. Lizenzen
| Material | Quelle | Lizenz |
|---|---|---|
| Stimme | Higgsfield ElevenLabs v4 Turbo (Preset Julian) | Higgsfield-Abo |
| 3D-Welt | eigene Blender-Szenen (engine/stadt.py + stadt_pfand.py) | eigen |
| 2D-Grafiken | engine/motion2d (Remotion), Karten Natural Earth / world-atlas | eigen / Public Domain |
| Thumbnail A/B | Higgsfield gpt_image_2_6 (1 Bild) | Higgsfield-Abo |
| Musik | assets/music (Unterbau-Bibliothek) | Higgsfield-Abo |
| Geräusche | sound-bibliothek: retail_scanner_1 (Freesound CC0, Beetlemuse), crushing_plastic_bottles (Freesound CC0, OleSouWester), banknote_counter, amb_factory, amb_night, sub_drop, tick, paper_flip, ub_hit, whoosh_slow_soft, diagram_whoosh, reveal_impact_01, ub_riser | CC0 / eigen |
| Pixabay-Videos | 19543, 5351, 152728, 12564, 202560, 69, 218339, 36473, 3178, 59138, 35574, 262213 | Pixabay Content License (ohne Marken/Logos geprüft) |

## Kosten
Stimme ≈ 32,3 Credits (10.598 Zeichen) + 1 Thumbnail-Bild 0,25 = **32,55 Credits** (Guthaben 2.401,16 → 2.368,61) (Bilder Blender, Clips Pixabay, Musik/Geräusche 0).

## Hochgeladen (27.11.2026)
Von Laurin freigegeben („Ja“), geplant für Sa 28.11.2026 19:00: https://www.youtube.com/watch?v=h4qaagII1kY
