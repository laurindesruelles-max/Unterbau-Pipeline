# Kanal „Unterbau“ – Grundsätze (aus Laurins Projektanweisung, Stand 17.11.2026)

**YouTube:** @unterbau26, Channel-ID UCVdWJ7R8vtn-ugpCh6wEJXw (seit 17.11.2026 mit vidIQ verbunden → Upload als geplanter Entwurf wie bei Goldsmith, 19:00 Uhr, erst nach Laurins „ja“ veröffentlichen).

**Claim:** Verstehen, wie die Welt funktioniert
**Versprechen:** Wie die Systeme funktionieren, von denen dein Leben abhängt – und was passiert, wenn sie ausfallen.
**Ziel:** 1 Mio. Abonnenten und 200.000 € Umsatz pro Monat in 3–4 Jahren.
**Sprache:** Deutsch. Zielgruppe 18–39 Jahre, Deutschland, Österreich, Schweiz.
**Anspruch:** Die Videos sollen aussehen und klingen wie animierte Kinofilme, mit durchgehender Spannungssteigerung und hoher Wiedergabezeit. Alles, was erzählt wird, muss stimmen und belegt sein.

## Kernprinzip
„Unterbau“ ist ein Blickwinkel, kein Themengebiet. Ein Thema passt nur, wenn mindestens zwei dieser Fragen spannend beantwortet werden:
1. Wie funktioniert es wirklich?
2. Wer verdient daran oder entscheidet?
3. Was passiert, wenn es ausfällt?

## Abgrenzung zu Simplicissimus
- Keine Themen, die Simplicissimus schon behandelt hat. Vor jeder Themenfreigabe vidIQ-Suche (`vidiq_youtube_search`) im Kanal UCKGMHVipEvuZudhHD05FOYA mit EINZELNEN Stichwörtern (mehrere Wörter liefern dort keine verlässlichen Treffer).
- Kein True Crime ohne System dahinter.
- Keine ähnlichen Titel, Namen oder Erkennungszeichen: Simplicissimus nutzt das „S“-Logo unten links, 1–2 Wörter in fetten Großbuchstaben und schwarze Augenbalken.
- Von Simplicissimus und fern übernehmen wir nur das Handwerk (Aufbau, Spannung, Satzbau), nie Themen oder Erkennungszeichen.

## Themen und Formate
- Etwa zwei Drittel weltweite Themen mit Bezug zum deutschsprachigen Raum, ein Drittel deutschlandspezifische Themen.
- Videos von 8–12 Minuten, nie unter 8 Minuten.
- Startformate: „Unterbau“ (Erklärstück), „Was wäre, wenn …“, „Der Moment, als …“. Weitere Formate, sobald sich die ersten bewährt haben.

## Skript
Verbindlich ist die Skript-Bibel: `SKRIPT_BIBEL.md` (Kopie des Claude-Docs https://claude.ai/artifact/EgyDonfjdZ24WtK7ck7rhk). 13 Regeln, Unterbau-Hook-Formel, Bauplan, Satzmuster, Checkliste vor der Freigabe. Kurzfassung:
- Kaltstart mitten in einer Szene im Präsens, die nach spätestens 5 Sekunden klar macht, worum es geht. Die Szene bricht im entscheidenden Moment ab, dann Rauszoomen und EINE Hauptfrage, die frühestens im letzten Drittel beantwortet wird.
- Hook-Mechanismen: Neugier-Lücke, Selbstbezug („du/dein“), offene Schleife, Geheimnis/Insiderwissen, Konflikt. KEIN Erwartungsbruch („alles ist anders, als du denkst“) als Hook.
- Schlüsselbild für die ersten 3–5 Sekunden zuerst festlegen, dann den Hook-Satz dazu schreiben. Satz, Bild, Texteinblendung und Ton sagen dasselbe.
- Ein roter Faden in Bewegung (Person ohne Gesicht, Objekt oder ein Tag). Erklärungen erst, wenn die Geschichte sie braucht.
- Hindernis-Kette, mindestens eine echte Rückblende des Versagens, jedes Kapitel endet mit einem Satz, der weiterzieht.
- Alle 30–45 Sekunden ein neuer Haken (im Drehbuch mit ▸). Kurze Sätze, in Szenen höchstens 14 Wörter. Jede Zahl mit Vergleich.
- Schluss: auflösen, durchatmen, Schritt in die Wirklichkeit, letzter Satz greift den Anfang auf, „Das war Unterbau.“
- **Ergänzung nach 003 (Laurin 20.11.2026, Vorlage `videos/003-supermarkt-leer/skript_v2.md`):**
  - **Du ist die Hauptfigur.** Dein Kühlschrank, dein Markt, deine Apotheke, dein Tank. Jedes Kapitel startet bei dir und kehrt zu dir zurück („Zurück zu dir.“).
  - **Die Spannungslinie läuft ab Minute 1 durch** (Countdown mit Uhrzeit: „Tag eins, achtzehn Uhr.“). Keine Hintergrund-Kapitel vor dem eigentlichen Versprechen.
  - **Höchstens eine harte Zahl alle ~20 Sekunden.** Keine Zahlenkolonnen.
  - **Ein Beispiel ausführlich als Szene statt vieler Fälle als Liste.** Weitere Fälle nur als Ein-Satz-Rückblende.
  - **2–3 echte Wendungen**, z. B. „Der Vorrat ist da, nur der Weg fehlt.“
  - **Satzrhythmus wechseln** (ein langer erzählender Satz, dann ein kurzer Schlag). Kein Dauer-Stakkato, keine Floskeln wie „Und hier wird es unbequem“.
  - **Jeder Absatz hat ein Bild-Ereignis** in [Klammern], am besten für die Miniaturwelt (`engine/miniwelt.py`). Was man nicht zeigen kann, fliegt raus.
  - **Vor dem Einsprechen ein unabhängiger Faktencheck** (Agent) gegen recherche.md und Live-Quellen. Er prüft Zuspitzungen, Vorwürfe als Vorwürfe und falsche Kausalität.
- Nachgestellte Szenen als „Szene nachgestellt“, Gedankenexperimente als „Gedankenexperiment“ kennzeichnen (Ton + Einblendung). Auch in fiktiven Szenen sind alle Fakten belegt.

## Stimme und Timing
- Feste Erzählerstimme: Julian, **nur noch über ElevenLabs v4 Turbo** (Laurin 19.11.2026: alle Kanäle nur ElevenLabs-Stimmen, die Higgsfield-Stimmen sprechen nicht alles sauber aus): `generate_audio_batch`, model `elevenlabs_v4_turbo`, `dialogue: [{text, voice_type: "preset", voice_id: "95429266-c0ac-4137-a209-63b8812b0f23"}]`, `use_unlim: false`. NICHT mehr `text2speech_v2`. Kosten ≈ 3 Credits pro 1.000 Zeichen. Pro Kapitel eine Datei, kurze Hook-Sätze dürfen einzeln eingesprochen werden. Zahlen und schwierige Namen ausschreiben („achtzehnhundertachtundfünfzig“, „C-Lion-1“).
- Wortgenaues Timing mit Parakeet (sherpa-onnx, kostenlos): `engine/wordtimes.py`. Satzzeiten werden NIE geschätzt.
- Mindestdauern: Kapitelkarte = eigene Pause 4,5 s, mind. 4 s sichtbar; Titelkarte mind. 4 s; Texteinblendung mind. 2,5 s; jedes Bild mind. 2 s (`engine/unterbau.py check`).

## Bildstil
- Realistisch-filmischer Look wie ein Kinofilm, kein Anime/Comic. Pro Video eine Look-Bibel (Lichtstimmung, feste Prompt-Bausteine: Motiv, Handlung, Kamera und Objektiv, Licht, Farbe, Material, Filmkorn, Verbote). Jeder Bild-Prompt bis ins Detail. Verbote immer anhängen: keine leuchtenden Kanten, keine Neon-Effekte, kein CGI-Glanz, kein lesbarer Text, keine Logos, keine sichtbaren Gesichter.
- Ein freigegebenes Bild dient als Stilreferenz für die weiteren Bilder.
- Markenzeichen in jedem Video: der **Querschnitt-Moment** – die Oberfläche wird durchsichtig oder reißt auf, man sieht das Innere des Systems. Im Einstieg und am Schluss. Umsetzung kostenlos mit `xsection` (zwei passende Bilder: Oberfläche + Innenansicht mit Bildreferenz).
- Ein oranger Akzent markiert das System – als echtes Licht oder Material, nie als Leuchteffekt.
- **Bewegung (neu 17.11.2026):** Es soll wirklich etwas passieren, aber ohne teure Kling-Clips: jede Einstellung bekommt 2.5D-Tiefenfahrt + Leben im Bild (Wasser schimmert, Licht atmet, Nebel, Schwebeteilchen, Regen). Echte Bewegung zusätzlich über kostenloses Stock-/Archivmaterial (`engine/stock.py`, Pixabay; `engine/sources.py`, Public Domain). KEINE KI-Videoclips (Kling, Seedance) – wie bei Goldsmith und Meisterwerk (Laurin 17.11.2026).
- Bilder bewusst abwechslungsreich (Nahaufnahme, Totale, Froschperspektive, Innenraum, Blick aus dem All); jede Einstellung ein eigenes Bild.

## Ton
- Geräusche zuerst aus Laurins gemeinsamer Sound-Bibliothek (`setup.sh` lädt sie: Text-Klick, Whoosh, Riser, Pop, …), dann `assets/sfx` (eigene, mit SOUNDS.md), dann kostenlos von Hugging Face (flreey/sfxmint-cc0-sound-effects); Higgsfield `mirelo_text_to_audio` nur als letzte Wahl (max. 2 pro Video). Nie per Code erzeugt. Piep- und Signaltöne 10–12 dB unter der Stimme.
- Musik: eigene Unterbau-Musik (nie Musik anderer Kanäle), filmisch und passend zum Spannungsbogen, taucht automatisch unter Julian ab. Ziel: einmalige Unterbau-Bibliothek in `assets/music` (5–7 Tracks, Laurin wählt per Hörprobe), danach keine Musikkosten mehr pro Video.

## Marke
- Profilbild: Querschnitt-Symbol – konzentrische Ringe in Weiß/Türkis auf Dunkelblau, oranger Kern, ein Segment herausgeschnitten (`assets/brand/profilbild.png`). Banner: `assets/brand/banner.png` (Logo + UNTERBAU + Claim, Erzeugung mit `engine/banner.py`).
- Thumbnail: Bild in Higgsfield ohne Text, Text danach als feste Vorlage (`engine/thumbnail.py`): dunkler halbdurchsichtiger Kasten rechts mit abgerundeten Ecken und orangem Balken links, Inter Display Black, erste Zeile weiß, Schlüsselwort orange, 2–3 Wörter in Groß-/Kleinschreibung. Nicht ins Bild gearbeitet, aber nicht leer oder aufgeklebt wirkend. 2–3 Varianten für „Test & Compare“.
- Verpackung: Titel und Thumbnail vor dem Skript. Vom Vertrauten ausgehen, Wissenslücke öffnen, „du/dein“, Verlust zeigen und am Ende auflösen, nur mit echter Recherche etwas enthüllen.

## Shorts
Aus jedem Video 5–7 eigenständige Shorts (kein „Teil 1/2“), 35–55 s, 1080×1920. Aufbau: (1) neuer Anfangssatz von Julian ohne Vorwissen, mit Frage oder Neugier-Lücke, dazu das stärkste Bild; (2) passende Sätze aus dem Video; (3) neuer Schlusssatz, der eine neue Frage öffnet und aufs ganze Video verweist. Neue Sätze nur mit belegten Fakten. Bild: das ganze Querformat in der Mitte mit Kamerabewegung, oben/unten dasselbe Bild unscharf und abgedunkelt; oben Aufhänger-Text und Zahlen, unten Untertitel mit wortgenauem Timing, kein Text auf dem Bild. Schlusskarte mit Profilbild und Verweis. Shorts-Skripte (Tabelle: Zeit, Julian sagt, Bild, Text oben) zuerst zur Freigabe. 1 Short pro Tag auf YouTube Shorts, TikTok, Instagram Reels (Facebook per Weiterleitung). Auf YouTube das Hauptvideo verknüpfen. Pro Short Titel, Kurztext, Hashtags in `Shorts_Texte.txt`.

## Plattformen, Kategorie, Playlists
- YouTube (Hauptkanal), TikTok, Instagram (Creator-Konto), Facebook-Seite. Überall derselbe Name und Profilbild B; Impressum per Link in der Bio.
- Kategorie immer „Bildung“.
- Playlists nach Themen, nicht nach Format („Internet & Daten – was unter der Oberfläche läuft“, „Geld & Bezahlen“, später „Energie & Strom“, „Wasser & Versorgung“, „Lieferketten & Logistik“). Passt keine, neue mit Titel + Beschreibung vorschlagen. Eigene Playlists für „Was wäre, wenn …“ und „Der Moment, als …“, sobald es mehrere Folgen gibt.

## Upload-Paket (immer vollständig)
Videotitel zum Kopieren + 1–2 Alternativtitel („Test & Compare“), Format, Kategorie, Playlist, Tags (15–25, komma-getrennt, unter 500 Zeichen, mit vidIQ abgesichert), fertiges Video (1080p MP4), 2–3 Thumbnails (1280×720), Videobeschreibung, 5–7 Shorts mit `Shorts_Texte.txt`; alles Textliche zusätzlich als `Upload_<Thema>.txt`.

## Quellen
Jede Zahl und Tatsachenbehauptung im Skript mit Link belegt. In der Beschreibung alle im Video verwendeten Quellen direkt mit Link, nach Kapiteln gruppiert – kein Link auf claude.ai-Dokumente, unter 5.000 Zeichen. Primärquellen bevorzugt. Fehler offen mit Zeitstempel in der Beschreibung korrigieren.

## Rechtssicherheit (Checkliste vor jedem Upload)
- Impressum im Kanal und per Link in der Bio auf TikTok, Instagram und Facebook.
- Werbung im Video ansagen, in der Beschreibung kennzeichnen, bei YouTube „Bezahlte Werbung“ aktivieren.
- KI-Kennzeichnung bei YouTube („Veränderte oder synthetische Inhalte“), bei TikTok und Instagram den KI-Schalter, Angabe in der Beschreibung (EU-KI-Verordnung, Art. 50).
- Nur selbst erzeugte Bilder und lizenzfreie bzw. selbst erzeugte Musik und Geräusche (dazu: Pixabay-Videos ohne Marken/Logos, Public-Domain-Archiv mit Nachweis); keine fremden Videos, Fotos oder Karten.
- Keine fremden Logos, keine Verwechslung mit Simplicissimus.
- Keine realistischen KI-Bilder echter Personen, keine sichtbaren Gesichter; nachgestellte Szenen und Gedankenexperimente gekennzeichnet; Vorwürfe nur mit Quelle; Meinung als Meinung erkennbar.
- Bei Gerichtsverfahren keine Namen Verurteilter, immer den Stand nennen („nicht rechtskräftig“), auch in Shorts; Stand kurz vor Upload erneut prüfen.
- Keine Anleitungen, die Schaden erleichtern (keine konkreten Schwachstellen von Infrastruktur).
- Claude ist kein Anwalt; Erstberatung im Medienrecht ist geplant (auch zu KI-Musik bei Monetarisierung und Impressum auf Social Media).

## Budget
So wenig wie möglich, höchstens 50 € pro Video (130 € ≈ 2.000 Credits, 1 Credit ≈ 0,065 €).
**Ziel wie Goldsmith/Meisterwerk (Laurin 17.11.2026): ca. 35–45 Credits pro Video, harte Obergrenze 45.** Stimme ~25 (nur einmal einsprechen, keine ganzen Neuaufnahmen), höchstens 60 KI-Bilder × 0,25 = 15 (die übrigen Einstellungen kostenlos: Pixabay-Clips, Public-Domain-Archiv), Thumbnails ~1, Shorts-Sätze ~2, Geräusche 0, Musik 0 (feste Bibliothek, nie pro Video neu), KI-Videoclips 0. Verbrauch während des Laufs mitzählen; droht die Grenze, Bilder durch kostenloses Material ersetzen statt mehr auszugeben.

## Zusammenarbeit
- Claude gibt eine klare Empfehlung mit Begründung, die Entscheidung trifft Laurin. Deutsch.
- Claude sagt ehrlich, wenn etwas unrealistisch ist, und kennzeichnet Schätzungen.
- Rückfragen nur an den Checkpoints (Thema/Titel/Thumbnail, Drehbuch, Hörprobe der ersten 2 Minuten, Shorts-Skripte, fertiges Video). In den automatischen Läufen alle 2 Tage (wie Goldsmith/Meisterwerk) wird nur bei Thema (2 h Fallback: Thema 1) und vor der Veröffentlichung („ja“) gewartet; Drehbuch, Hörprobe und Shorts-Skripte gehen dort nur zur Info an Laurin.
- Businessplan (aktuelle Fassung): https://claude.ai/artifact/GSNjdvARppGm6PHraEhd8N
