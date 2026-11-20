"""Ton fuer die Unterbau-Stilprobe, Version 2 (Laurin 20.11.: die Klacks klangen wie Schuesse -> raus).
Stromausfall jetzt als Brummen, das in der Tonhoehe abfaellt und erstirbt, keine harten Einzelschlaege. Sound-Plan (8 Stellen, jede an einem Bild-Ereignis):
Regen (sichtbar) + leises Stadtbrummen als Bett | Uhr springt 3x (Fallblatt) | 18:00: Musik bricht ab, tiefer Treffer
Lichter gehen aus: 3 Schalter-Klacks, das Brummen reisst mit dem letzten Block ab | "Dein Haus": leiser Whoosh
Dein Fenster geht aus: Klack + tiefer Drop | danach dunkle Musik leise zurueck."""
import sys; sys.path.insert(0, "/home/claude/stilproben")
from mixer import mix
U = "/home/claude/repos/Unterbau-Pipeline/assets/"; X = "/home/claude/ub_sfx/"
hum, rain = X + "fire_electric_hum_39.wav", X + "amb_rain.wav"
ev = [(1.5, X + "paper_flip.wav", 0.45), (3.0, X + "paper_flip.wav", 0.45), (4.5, X + "paper_flip.wav", 0.45),
      (6.0, X + "paper_flip.wav", 0.5), (6.02, U + "sfx/sub_drop.wav", 0.9),
      (10.6, U + "sfx/whoosh_slow_soft.wav", 0.22),
      (12.2, U + "sfx/ub_drop.wav", 0.3)]
music = [(hum, 0.08, 0.0, 1.0, 0.15, [], 0, 6.0), (X + "hum_stromausfall.wav", 0.2, 5.9, 0.1, 0.3, [], 0, 10.5),
         (rain, 0.14, 0.0, 1.0, 0.6, [], 0, 9.0), (rain, 0.14, 8.4, 0.6, 1.0, [], 0.5, 15.0),
         (U + "music/ub_system_puls.mp3", 0.45, 0.0, 0.6, 0.2, [], 30.0, 5.95),
         (U + "music/ub_ausfall_dunkel.mp3", 0.32, 8.0, 1.5, 1.0, [(12.2, -10, 0.5)], 10.0, 15.0)]
print(mix("/home/claude/stilproben/stilprobe_unterbau.mp4", "/home/claude/stilproben/ton_unterbau_v2.mp4", ev, 15.0, music))
