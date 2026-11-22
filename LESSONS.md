# LESSONS – Unterbau (feste Regeln, Erkenntnisse, Video-Log)

> **Seit 20.11.2026 zuerst lesen:** `HANDWERK.md` (Regeln für alle Kanäle) und `EFFEKTE.md` (Handschrift und erlaubte Effekte dieses Kanals, von Laurin abgenommen). Bei Widerspruch gelten diese beiden Dateien.


Jeder Lauf liest diese Datei vor der Produktion und befolgt sie. Neue Erkenntnisse und Laurins Entscheidungen hier eintragen (mit Datum).

## Feste Regeln (Laurin)
- Videos IMMER über 8 Minuten (Ziel 8:30–10:30, 1.300–1.600 Wörter). Fertiges Video mit ffprobe prüfen; unter 8:00 nicht abgeben, sondern verlängern.
- Skript nach `SKRIPT_BIBEL.md`; vor der Freigabe prüft ein Kritiker-Agent (Agent-Tool) das Drehbuch gegen die Checkliste und jede Behauptung gegen die Quellen.
- Timing NIE schätzen: `engine/wordtimes.py` (Parakeet). Einblendungen exakt auf das Schlüsselwort.
- Mindestdauern: Bild ≥ 2 s, Einblendung ≥ 2,5 s, Kapitelkarte eigene Pause 4,5 s, Titelkarte ≥ 4 s (`python3 engine/unterbau.py <work> check`).
- Einfache Prompts sehen nach KI aus → jeder Bild-Prompt bis ins Detail (Ort, Gegenstände, Material, Lichtquelle und -richtung, Objektiv, Bildausschnitt) + Look-Block + Verbotsliste.
- Per Code erzeugte Geräusche klingen billig → nie selbst synthetisieren.
- Ohne offene Frage im Einstieg wirkt das Video langweilig (Kartenzahlung-Video).
- Shorts brauchen einen eigenen Einstieg ohne Vorwissen.
- Musik ist kanal-eigen: nie Goldsmith-/Meisterwerk-Musik verwenden (Laurin 17.11.2026).
- **Kosten wie Goldsmith/Meisterwerk (Laurin 17.11.2026):** 35–45 Credits pro Video, nie mehr als 45. KEINE KI-Videoclips (auch nicht für den Höhepunkt), KEINE neue Musik pro Video (nur assets/music; neue Tracks nur auf Laurins ausdrücklichen Wunsch), höchstens 60 KI-Bilder (Rest kostenlos über Pixabay/Public Domain), Geräusche kostenlos (gemeinsame Bibliothek → assets/sfx → Hugging Face CC0; mirelo nur letzte Wahl). Unter 45 Credits Guthaben: Laurin bitten aufzuladen und stoppen.
- **Stimme (Laurin 19.11.2026):** Julian nur noch über ElevenLabs v4 Turbo (`elevenlabs_v4_turbo`, Preset-Voice 95429266-…). Gilt für alle Kanäle: nur ElevenLabs-Stimmen, keine Higgsfield-`text2speech_v2`-Stimmen mehr (Aussprache). Eleven v4 (voll) wäre ~4,6 Credits/1.000 Zeichen (~40 pro Video) → Turbo gewählt.
- **Lebendiger Schnitt (Laurin 19.11.2026: „so langweilig“):** Standbilder mit langsamer Fahrt und 8 s pro Bild sind zu ruhig. Schnitt alle 3–4 s, animierte Grafiken (Karten, Zähler, Ablauf-Ketten), echte Pixabay-Clips, mehr Bewegung im Bild und Schnitt-Sounds.
- **Sounds vorher anhören (Laurin 19.11.2026: Grafik-Sound „Müll“):** ub_daten (Quietsch-/Piepton) und ub_klick (Kamera-Auslöser) nicht mehr verwenden. Jeden Effekt vor dem Einbau mit `earshot describe` prüfen und die Effektspur mit `earshot timeline` durchhören. Grafik kommt rein = diagram_whoosh, Zahl landet = reveal_impact_01, Text = whoosh_slow_soft leise.
  - **Klarstellung (Laurin 22.11.2026):** Piep- und Daten-Töne sind nicht grundsätzlich verboten – nur schlechte. Gesperrt sind genau diese zwei Dateien (Sperrliste in sound-bibliothek/profiles.json). Neue Daten-Töne sind erlaubt, wenn sie im earshot-/Gemini-Casting gut abschneiden.
- **Rhythmus (Laurin 17.11.2026):** alle 2 Tage ein Video wie bei Goldsmith und Meisterwerk.

## Umstellung 17.11.2026 (Laurin): GitHub statt Claude-Projekt, günstig statt Kling
- Alles liegt in diesem Repo; ein neues Video geht aus jedem Chat mit dem Skill `unterbau-video`.
- Laurin: „die Videos werden komplett animiert bei Higgsfield und kosten mega viel Geld“ → Bewegung jetzt kostenlos mit der Goldsmith-Technik (2.5D-Tiefenfahrt + Leben im Bild + Querschnitt-Effekt). Kling seit 17.11.2026 gar nicht mehr (Kosten wie die anderen Kanäle).
- Bilder mit gpt_image_2_6 Standard (0,25 Credits), nicht mehr „high“ (1,5 Credits).
- Pilot-Intro (Seekabel-Kaltstart, 75 s) als Look-Test gebaut: `videos/001-seekabel-pilot/spec.json`. Kosten 27,6 Credits (Stimme 66 s, 17 Bilder, 1 Musikstück 100 s, 4 Geräusche). Laurins Urteil: (offen).

## Technik-Erkenntnisse
- Querschnitt-Moment: Innenbild mit `medias: [{value: <job_id Oberflächenbild>, role: image_references}]` und „exactly the same camera position, framing and composition“ erzeugen; Komposition passt nicht 100 %, die Enthüllung von oben nach unten (xsection) kaschiert das.
- Parakeet erkennt zusammengezogene Sätze („Durchs All tun sie …“) – der Abgleich mit dem Skripttext (difflib) fängt das ab.
- Rendern: Pilot (75 s, 1.880 Frames) brauchte ~11 Min. mit 3 Prozessen auf 2 Kernen → ein 10-Min.-Video ≈ 1,5 h. In 3 Abschnitten parallel rendern (`--from/--to`, nohup), Fortschritt pollen, dann zusammenfügen.

## Offen / nächste Schritte
- Musik-Bibliothek: 17.11.2026 auf Laurins Wunsch 4 Tracks erzeugt (87 Credits einmalig, siehe assets/music/MUSIK.md), alle 4 von Laurin abgenommen. NICHT mehr pro Video Stücke erzeugen; je Kapitel passenden Track aus der Bibliothek wählen, Musikpausen bewusst einsetzen.
- Shorts-Pipeline als Skript ins Repo (bisher pro Video mit ffmpeg gebaut).
- Profilbild (vom YouTube-Kanal zurückgeholt) und Banner liegen seit 17.11.2026 in assets/brand/ (Banner neu, seit 17.11.2026 auf YouTube aktiv, 0 Credits: `python3 engine/banner.py assets/brand/profilbild.png assets/brand/banner.png`).

## Video-Log
| Nr. | Titel | Status | Erkenntnisse |
|---|---|---|---|
| 001 | Das Kabel am Meeresgrund, an dem dein Internet hängt | fertig + abgenommen (09.11.2026), 9:07 Min., 7 Shorts, ~215 Credits | mehr echte Bewegung statt Standbilder; Timing per Spracherkennung messen; Shorts mit eigenem Einstieg. Recherche: https://claude.ai/artifact/2YiRjq3QSPVMRZYjD9HfQV · Skript: https://claude.ai/artifact/D1k4smGrysZTUVJmhkKNDH |
| 002 | Was passiert, wenn deine Karte plötzlich nicht mehr geht | produziert (v2, 6 Shorts), Laurin: zu langweilig | daraus Kino-Stil + Skript-Bibel. Recherche: https://claude.ai/artifact/6sdhBxRn5mGdb1KuTEnWn3 · Skript: https://claude.ai/artifact/RtwMUcB9KcvoginUC1C2oP · Kino-Test-Drehbuch: https://claude.ai/artifact/1uAWKoP8jVQ7PySScZo2j2 |
| 003 | Warum dein Supermarkt nach 3 Tagen leer wäre | produziert 19.11.2026, 9:53 Min., 6 Shorts, YouTube-Entwurf für 21.11. 19:00 (wartet auf Laurins „ja“) | **44,0 Credits** (Stimme 26,4 + 2 Korrektursätze 0,5 + Shorts-Sätze 2,85 + 58 Bilder 14,5; Musik/Geräusche 0). Thema von Laurin gewählt (Nr. 2). Kritiker-Agent: 28 Änderungen; Faktencheck: Spanien-Satz korrigiert (neu eingesprochen, gleiche Länge eingepasst). Drehbuch: https://claude.ai/artifact/B5673NgjsEXn2Juv8TPSGT |
| Pilot | Seekabel-Kaltstart im neuen Look (ohne Kling) | 17.11.2026 Look-Test | siehe oben |

## Ton & Musik mit audiokit (Laurin 18.11.2026)
Problem: Soundeffekte oft unpassend/billig, Musik zu gleichförmig – Laurin schaut die eigenen Videos nicht zu Ende. vidIQ-Auswertung 18.11.: größter Absprung in den ersten ~30 s; Musik läuft 1,5–3 Min. gleich durch, kein Spannungsaufbau vor Enthüllungen; Passagen von 25–60 s ohne neuen Reiz.
- `setup.sh` lädt audiokit (Repo sound-mediathek) nach /home/claude/audiokit. Die Engine nutzt es automatisch und schreibt `ton_bericht.txt` – Bericht in qa.md übernehmen.
- Sounds werden vor dem Mischen aufgeräumt: gleiche Lautheit, Einblendungs-Sounds nicht im Dauerfeuer, max. 2 Sounds gleichzeitig, keine Endlos-Schleifen, defekte Dateien fliegen raus. Geräusche zu sichtbarer Bewegung bleiben.
- Musik nach Spannungskurve: Wechsel der Stelle/des Tracks spätestens alle ~60–80 s, Anschwellen vor Enthüllungen/Zahlen, Bogen pro Kapitel, Pegel automatisch unter der Stimme. Weiterhin nur die eigene Musik-Bibliothek, keine neuen Tracks.
- Im Skript Enthüllungen klar formulieren (Zahl, „aber“, „doch“, Frage → Antwort): daraus baut die Spannungskurve.
- Bericht meldet Lücken > 22 s ohne neuen Reiz → dort Bild/Effekt/Schnitt ergänzen, bevor gerendert wird.

## Hook-Regeln (Laurin 19.11.2026 – gilt ab dem nächsten Video)
Grundlage: Auswertung erfolgreicher Ausreißer-Videos in allen 5 Nischen (vidIQ), Hook-Studie mit über 4.000 Hooks aus Videos mit über 1 Mio. Aufrufen, Aprilynne Alters Intro-Formel. Es gibt keinen einzelnen besten Hook-Typ – aber alle erfolgreichen Hooks haben diesen Aufbau:
1. **Thema in 0–5 s gesagt UND gezeigt** – genau das, was Titel und Thumbnail versprechen; das Thumbnail-Motiv ist im ersten Bild zu sehen. Kein Datum, kein Logo, keine Vorrede als erster Satz.
2. **Offene Frage / Rätsel spätestens bei 10–15 s.** Die Antwort kommt frühestens im letzten Drittel.
3. **Konkretes Versprechen vor Hook-Ende** (was man am Ende weiß, wie viele Punkte, wer dahintersteckt).
4. **Bestes Material zuerst:** die stärkste Animation / das stärkste Bild gehört in den Hook.
5. **Kurz:** Hook-Länge siehe Kanal-Regel unten. Kontext erst danach, nicht vorne stapeln.
6. **Rehook:** Jedes Kapitel endet mit einer neuen offenen Frage.

**Prüfung vor dem Rendern** (in qa.md eintragen): Sekunde, ab der das Thema klar ist (≤ 5), Sekunde der offenen Frage (≤ 15), Versprechen ja/nein, Hook-Länge (Wörter ÷ 2,4 = Sekunden).
**Nach 48 h:** Retention bei 30 s per vidIQ (audience_retention) ins Video-Log. Ziel ≥ 70 %. Unter 50 % → beim nächsten Video den Alternativ-Typ unten nehmen.
**Unterbau-Hook:** Die Hook-Formel der SKRIPT_BIBEL.md bleibt verbindlich (Kaltstart, Neugier-Lücke, Selbstbezug, kein Erwartungsbruch). Ergänzung: Das Rätsel steht im ersten Satz und ist ohne Vorwissen verständlich (Vorbild: „Jede Minute zuckt das Stromnetz.“). **Länge bis zur Titelkarte ≤ 45 s.**

## Sound-Bibliothek aus Laurins Sammlung (19.11.2026)
- setup.sh lädt `bibliothek/unterbau/` (NUR die Effekte dieses Kanals) + `bibliothek/gemeinsam/` (Foley, Atmos, Waffen) nach /home/claude/sfx-bibliothek/bibliothek. Liste: `bibliothek/unterbau/LISTE.md` im Repo sound-mediathek.
- **Reihenfolge bei der Sound-Wahl:** 1. eigene assets/sfx (abgenommen) → 2. Bibliothek (`import bibliothek as BIB; BIB.pick("unterbau", "whoosh", seed=<video-ordner>)`, `BIB.suche("auto")`) → 3. Hugging Face/SFXMint nur, wenn nichts passt.
- `seed` = Video-Ordner: so wechseln die Sounds von Video zu Video, ohne dass es zufällig klingt. Alle Bibliotheks-Sounds sind geprüft (audit.py), Memes/geschützte/kommerzielle Sounds sind aussortiert.
- Nie Effekte aus fremden Kanal-Ordnern nehmen; `reserve/` nur nach Rückfrage bei Laurin.

## Erkenntnisse Video 003 (19.11.2026)
- Kosten real: Julian ≈ 3 Credits pro 1.000 Zeichen (8.750 Zeichen = 26,4). Mit 58 Bildern und 6 Shorts liegt ein 10-Min.-Video bei ~44 Credits – mehr Bilder oder neu eingesprochene Kapitel sprengen die Grenze. Shorts-Sätze kurz halten (~2,9 Credits für 12 Sätze).
- Higgsfield-Guthaben wird von mehreren Kanälen geteilt: am 19.11. gingen parallel 65 Credits für Musik eines anderen Laufs ab. Vor großen Schritten `balance` + `transactions` prüfen.
- gpt_image_2_6 liefert 1344×752; mit „gentle vignette“ malt es oft einen dunklen, abgerundeten Bildrand → alle Bilder vor dem Rendern 3 % beschneiden und auf 1920×1080 skalieren (in script.md beschrieben). Rate-Limit: höchstens 8 Bilder pro Batch.
- Einzelne Sätze nachträglich korrigieren, ohne neu zu rendern: neuen Satz einsprechen, in die alte Lücke mit Stille einpassen (gleiche Länge), Wortzeiten neu, `dur` der alten words-Datei behalten, Ton neu mischen, mit dem fertigen Bild neu muxen.
- Spracherkennung am fertigen Ton fand „Deutschland häldöl“ (verschluckt) → Satz umformuliert („lagert Erdöl“). Verbindungen wie „hält Erdöl“ vermeiden.
- Rendern: 3 Abschnitte parallel auf 2 Kernen ≈ 45–57 Min. für 9:53. `--to` über das Ende hinaus rendert Leerlauf → beim Zusammenfügen mit `-t <Länge>` kappen.
- Neues Werkzeug `engine/shorts.py` (Shorts aus dem fertigen Video: neuer Einstieg/Schluss, Wortzeit-Untertitel, Blur-Hintergrund, Schlusskarte).
- mcp.vidiq.com ist vom Sandbox-Proxy gesperrt → Thumbnail erst per Higgsfield `media_upload` hochladen und die öffentliche URL an `vidiq_upload_image` geben.
- Pixabay-Schlüssel war nicht verfügbar → alles über KI-Bilder (58) gelöst.

## Ohren (19.11.2026, Laurin: „du hast keine Ohren … weit entfernt von Netflix“)
- **Referenzprofil:** `assets/doku_profil.json` = earshot-Profil aus fern (NATO), Simplicissimus (Kanzler, Nord Stream) und Netflix „Our Planet“ (je 10 Min., nur gemessen, nicht verwendet). Pflicht vor jeder Abgabe: `earshot critique <video> --profile assets/doku_profil.json` → Ziel „launch-grade“, 0 major.
- **Gemini hört mit:** `GEMINI_API_KEY=… earshot llm <datei> --yes-upload [--prompt …]` (Schlüssel nur zur Laufzeit; kostenlose Stufe = nur Flash-Modelle, Pro ist gesperrt). Gemini hört 16 kbps mono: Sub-Bass und Stereo hört es nicht, Zischlaute der Stimme hält es für „Glockenspiel“. Die Gesamtnote ist hart und schwankt (fern bekommt auch 5/10) → Gemini für **Casting** (Kandidaten vergleichen) und Fundstellen nutzen, das Profil für die Messung.
- **Sound-Casting mit Gemini (19.11.):** Grafik kommt rein = `ub_whoosh` (PREMIUM), Alternative `whoosh_slow_soft` (PREMIUM); Zahl/Enthüllung landet = `sub_drop` oder `ub_hit` (PREMIUM); Zähler = `tick`-Folge wie Goldsmith (PREMIUM). CHEAP: transform_grow/morph, data_countup_long, click_mouse_soft-Folge, ub_drop als Zahl-Sound, cinematic_boom_01.
- **Musik:** Gemini einzeln: ub_kaltstart_meer 9/10 („wie Max Richter, passt zu fern/Simplicissimus“), ub_spannung_aufbau 6–7.5, ub_system_puls = Akustikgitarre/Folk, passt nicht zu Technik-Spannung → nur noch für ruhige Momente.
- **Mix-Fehler gefunden und behoben:** audiokit-Musik wechselte alle 60–80 s Track/Stelle mit 19 Stopps/Min. (Profis 4–8) → neuer Modus `music: {"mode": "kapitel"}` (ein Stück pro Kapitel, Musik trägt unter Kapitelkarten +7 dB, Anschwellen vor Enthüllungen, Stopps nur bewusst). Einstufiges `loudnorm` quetschte die Dynamik → `master()`: EQ (Sub, 2,5 kHz, Präsenz), lineare Verstärkung + Spitzenbegrenzer (−3 dBFS, sonst AAC-Überschwinger). Bewusste Höhepunkte als `hits` (werden vom Aufräumen nicht leiser gemacht).
- Ergebnis Vorschau 003: earshot-Profilvergleich 17/23 → **22/23 (launch-grade, 0 major)**.
