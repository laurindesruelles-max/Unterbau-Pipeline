# LESSONS – Unterbau (feste Regeln, Erkenntnisse, Video-Log)

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
| Pilot | Seekabel-Kaltstart im neuen Look (ohne Kling) | 17.11.2026 Look-Test | siehe oben |

## Ton & Musik mit audiokit (Laurin 18.11.2026)
Problem: Soundeffekte oft unpassend/billig, Musik zu gleichförmig – Laurin schaut die eigenen Videos nicht zu Ende. vidIQ-Auswertung 18.11.: größter Absprung in den ersten ~30 s; Musik läuft 1,5–3 Min. gleich durch, kein Spannungsaufbau vor Enthüllungen; Passagen von 25–60 s ohne neuen Reiz.
- `setup.sh` lädt audiokit (Repo sound-mediathek) nach /home/claude/audiokit. Die Engine nutzt es automatisch und schreibt `ton_bericht.txt` – Bericht in qa.md übernehmen.
- Sounds werden vor dem Mischen aufgeräumt: gleiche Lautheit, Einblendungs-Sounds nicht im Dauerfeuer, max. 2 Sounds gleichzeitig, keine Endlos-Schleifen, defekte Dateien fliegen raus. Geräusche zu sichtbarer Bewegung bleiben.
- Musik nach Spannungskurve: Wechsel der Stelle/des Tracks spätestens alle ~60–80 s, Anschwellen vor Enthüllungen/Zahlen, Bogen pro Kapitel, Pegel automatisch unter der Stimme. Weiterhin nur die eigene Musik-Bibliothek, keine neuen Tracks.
- Im Skript Enthüllungen klar formulieren (Zahl, „aber“, „doch“, Frage → Antwort): daraus baut die Spannungskurve.
- Bericht meldet Lücken > 22 s ohne neuen Reiz → dort Bild/Effekt/Schnitt ergänzen, bevor gerendert wird.
