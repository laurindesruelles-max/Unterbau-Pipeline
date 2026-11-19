# Unterbau-Pipeline

YouTube-Kanal **Unterbau** (@unterbau26, UCVdWJ7R8vtn-ugpCh6wEJXw) – „Verstehen, wie die Welt funktioniert“. Deutsch, 8–12 Minuten, realistisch-filmischer Look.
Ein neues Video geht aus **jedem** Claude-Chat mit dem Skill `unterbau-video` (Repo klonen, dieser README + LESSONS.md folgen).

| Datei | Inhalt |
|---|---|
| `KANAL.md` | Grundsätze des Kanals (Kernprinzip, Abgrenzung, Stil, Stimme, Shorts, Upload-Paket, Recht, Budget) |
| `SKRIPT_BIBEL.md` | verbindliche Skript-Regeln, Hook-Formel, Bauplan, Checkliste, Satzmuster |
| `LESSONS.md` | feste Regeln, Erkenntnisse, Video-Log – vor jeder Produktion lesen |
| `engine/` | Werkzeuge (siehe unten) |
| `assets/sfx`, `assets/music` | eigene Geräusche (Herkunft in SOUNDS.md) und eigene Unterbau-Musik |
| `videos/NNN-slug/` | pro Video: spec.json, script.md, Beschreibung, Thumbnails (KEINE Audio-/Bild-/Videodateien) |

## Ablauf (Checkpoints = nur dort Laurin fragen)
1. **Thema + Titel + Thumbnail-Idee** (Checkpoint 1): 3 Vorschläge, je ≥ 2 der 3 Unterbau-Fragen, vorher Simplicissimus-Check mit vidIQ (einzelne Stichwörter). Titel mit `vidiq_score_title`.
2. **Recherche** (Primärquellen, jede Zahl mit Link) → Claude-Doc „Recherche: <Thema>“.
3. **Skript** nach SKRIPT_BIBEL.md: Geschichte in 5 Sätzen → Spannungsplan → Drehbuch-Tabelle pro Satz (Julian sagt | Bild | Ton | Text | Haken ▸) → Kritiker-Agent → 2 Varianten für Einstieg und Höhepunkt → **Freigabe** (Checkpoint 2, Claude-Doc).
4. **Hörprobe** der ersten 2 Minuten (Checkpoint 3), dann Rest einsprechen (Julian, pro Kapitel eine Datei).
5. `sh setup.sh videos/NNN-slug /home/claude/unterbau-work`, Stimme nach `audio/`, dann Wortzeiten:
   `python3 engine/wordtimes.py audio/1.mp3 text1.txt words/w1.json` (Text = exakt der eingesprochene Text).
6. **Look-Bibel + Bilder**: gpt_image_2_6 (0,25 Credits), 16:9, je Einstellung ein eigenes Bild `img/NN.png` (höchstens 60 KI-Bilder pro Video, Rest kostenlos über Pixabay/Public Domain), in Wellen zu 4, Stilreferenz per `image_references`. Querschnitt-Paar: Oberflächenbild + Innenbild mit Bildreferenz. Kontaktbogen ansehen, Schwaches neu.
7. **spec.json** schreiben (Vorlage `videos/001-seekabel-pilot/spec.json`):
   - `parts`: Tonspuren mit Wortzeiten, dazwischen `{"chapter": {"n", "title", "pause": 4.5}}`
   - `shots`: `{"img", "at": [teil, "Wort(e)", versatz], "move": push|pull|left|right|rise|orbit|{dx,dy,z0,z1,par}, "fx": [wet, fog, cars, flash, screens, money, cold, rays], "atmo": dust|rain|snow}`; Querschnitt: `{"xsection": [oben, innen], "reveal": anker, "waterline": 0.4}`; Schwarzbild `{"black": true}`. Anker `[teil, "END", versatz]` = Ende der Tonspur.
   - `overlays`: `bauchbinde` (lines), `zahl` (big, sub), `hinweis` („Szene nachgestellt“), `videotitel` (lines); `title` = Titelkarte UNTERBAU + Claim
   - `sfx` [anker, name, gain], `amb` [von, bis, name, gain], `music` {file, gain, rests}
8. `python3 engine/unterbau.py <work> check` (Mindestdauern), `still <sek…>` an 8–10 Stellen ansehen, dann rendern in 3 Abschnitten parallel (`--from A --to B --out teil.mp4`), Ton mit `audio <out.wav>`, zusammenfügen (ffmpeg concat + Ton).
9. **Prüfen**: Kontaktbogen (15–20 Frames), Länge ≥ 8:00, Spracherkennung am fertigen Ton, Faktencheck-Agent, Rechts-Checkliste (KANAL.md). Fertiges Video an Laurin (Checkpoint 4).
10. **Shorts** (Skripte zuerst zur Freigabe, Checkpoint 5), **Thumbnails** (`python3 engine/thumbnail.py bild.png out.jpg "Nur ein" "Kabel."`), **Upload-Paket** (KANAL.md).
11. Projektdateien committen + pushen, LESSONS.md-Video-Log ergänzen.

## Engine
| Werkzeug | Zweck | Kosten |
|---|---|---|
| `engine/unterbau.py` | Compositor: 2.5D-Fahrt, Leben im Bild, Querschnitt, Overlays im Unterbau-Look, Ton-Mix (Musik taucht unter Julian ab, −14 LUFS) | 0 |
| `engine/wordtimes.py` | Wortzeiten per Parakeet (sherpa-onnx) + Abgleich mit Skript | 0 |
| `engine/depth25d.py`, `engine/cinemagraph.py` | Tiefen-Parallaxe, Licht/Wasser/Nebel/Regen-Animation (aus goldsmith-pipeline) | 0 |
| `engine/stock.py`, `engine/sources.py` | echtes Videomaterial (Pixabay, Schlüssel bei Laurin) und Public-Domain-Archiv | 0 |
| `engine/thumbnail.py` | Thumbnail-Vorlage | 0 |
| `engine/qa.py` | Technik-Prüfung (Länge, Lautheit, Kontaktbogen) | 0 |
| `engine/motion.py` | Schnitt-Tempo (`"cut": 3.4` teilt lange Einstellungen in Ausschnitte) + animierte Grafiken: `karte`, `balken`, `zaehler`, `tage`, `ablauf`; echte Clips als Shot `{"clip": "vid/x.mp4"}` | 0 |
| `engine/shorts.py` | 5–7 Shorts aus dem fertigen Video (neuer Einstieg/Schluss von Julian, Untertitel mit Wortzeiten, Schlusskarte) | nur die neuen Sätze |

Credits pro Video: **Ziel 35–45, Obergrenze 45** wie Goldsmith/Meisterwerk (Stimme ~25, max. 60 Bilder = 15, Thumbnails ~1, Shorts-Sätze ~2). Keine KI-Videoclips, keine Musik pro Video (feste Bibliothek in assets/music), Geräusche kostenlos. Automatischer Lauf alle 2 Tage (Scheduled Task „Unterbau-Video alle 2 Tage“).
