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

## Umstellung 17.11.2026 (Laurin): GitHub statt Claude-Projekt, günstig statt Kling
- Alles liegt in diesem Repo; ein neues Video geht aus jedem Chat mit dem Skill `unterbau-video`.
- Laurin: „die Videos werden komplett animiert bei Higgsfield und kosten mega viel Geld“ → Bewegung jetzt kostenlos mit der Goldsmith-Technik (2.5D-Tiefenfahrt + Leben im Bild + Querschnitt-Effekt). Kling nur noch 2–3 Clips für den Höhepunkt und nur nach Freigabe.
- Bilder mit gpt_image_2_6 Standard (0,25 Credits), nicht mehr „high“ (1,5 Credits).
- Pilot-Intro (Seekabel-Kaltstart, 75 s) als Look-Test gebaut: `videos/001-seekabel-pilot/spec.json`. Kosten 27,6 Credits (Stimme 66 s, 17 Bilder, 1 Musikstück 100 s, 4 Geräusche). Laurins Urteil: (offen).

## Technik-Erkenntnisse
- Querschnitt-Moment: Innenbild mit `medias: [{value: <job_id Oberflächenbild>, role: image_references}]` und „exactly the same camera position, framing and composition“ erzeugen; Komposition passt nicht 100 %, die Enthüllung von oben nach unten (xsection) kaschiert das.
- Parakeet erkennt zusammengezogene Sätze („Durchs All tun sie …“) – der Abgleich mit dem Skripttext (difflib) fängt das ab.
- Rendern: Pilot (75 s, 1.880 Frames) brauchte ~11 Min. mit 3 Prozessen auf 2 Kernen → ein 10-Min.-Video ≈ 1,5 h. In 3 Abschnitten parallel rendern (`--from/--to`, nohup), Fortschritt pollen, dann zusammenfügen.

## Offen / nächste Schritte
- Eigene Musik-Bibliothek (5–7 Tracks, ~85 Credits einmalig), Laurin wählt per Hörprobe. Bis dahin pro Video 1–3 Stücke erzeugen.
- Shorts-Pipeline als Skript ins Repo (bisher pro Video mit ffmpeg gebaut).
- Profilbild B_Querschnitt.png und Banner ins Repo legen (assets/brand/), Laurin schickt die Dateien.

## Video-Log
| Nr. | Titel | Status | Erkenntnisse |
|---|---|---|---|
| 001 | Das Kabel am Meeresgrund, an dem dein Internet hängt | fertig + abgenommen (09.11.2026), 9:07 Min., 7 Shorts, ~215 Credits | mehr echte Bewegung statt Standbilder; Timing per Spracherkennung messen; Shorts mit eigenem Einstieg. Recherche: https://claude.ai/artifact/2YiRjq3QSPVMRZYjD9HfQV · Skript: https://claude.ai/artifact/D1k4smGrysZTUVJmhkKNDH |
| 002 | Was passiert, wenn deine Karte plötzlich nicht mehr geht | produziert (v2, 6 Shorts), Laurin: zu langweilig | daraus Kino-Stil + Skript-Bibel. Recherche: https://claude.ai/artifact/6sdhBxRn5mGdb1KuTEnWn3 · Skript: https://claude.ai/artifact/RtwMUcB9KcvoginUC1C2oP · Kino-Test-Drehbuch: https://claude.ai/artifact/1uAWKoP8jVQ7PySScZo2j2 |
| Pilot | Seekabel-Kaltstart im neuen Look (ohne Kling) | 17.11.2026 Look-Test | siehe oben |
