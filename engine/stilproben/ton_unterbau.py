"""Ton fuer die Unterbau-Stilprobe. Sound-Plan (8 Stellen, jede an einem Bild-Ereignis):
Regen (sichtbar) + leises Stadtbrummen als Bett | Uhr springt 3x (Fallblatt) | 18:00: Musik bricht ab, tiefer Treffer
Lichter gehen aus: 3 Schalter-Klacks, das Brummen reisst mit dem letzten Block ab | "Dein Haus": leiser Whoosh
Dein Fenster geht aus: Klack + tiefer Drop | danach dunkle Musik leise zurueck."""
import sys; sys.path.insert(0, "/home/claude/stilproben")
from mixer import mix
U = "/home/claude/repos/Unterbau-Pipeline/assets/"; X = "/home/claude/ub_sfx/"
hum, rain = X + "fire_electric_hum_39.wav", X + "amb_rain.wav"
ev = [(1.5, X + "paper_flip.wav", 0.45), (3.0, X + "paper_flip.wav", 0.45), (4.5, X + "paper_flip.wav", 0.45),
      (6.0, X + "paper_flip.wav", 0.5), (6.02, U + "sfx/reveal_impact_01.wav", 1.3), (6.02, U + "sfx/sub_drop.wav", 0.7),
      (6.5, X + "door_lock_01.wav", 0.85), (7.3, X + "door_lock_01.wav", 0.8), (8.1, X + "door_lock_01.wav", 0.75), (8.9, X + "door_lock_01.wav", 0.7), (9.7, X + "door_lock_01.wav", 0.65), (10.4, X + "door_lock_01.wav", 0.6),
      (10.6, U + "sfx/whoosh_slow_soft.wav", 0.25),
      (12.2, X + "door_lock_01.wav", 0.5), (12.22, U + "sfx/ub_drop.wav", 0.35)]
music = [(hum, 0.07, 0.0, 1.0, 0.3, [], 0, 6.0), (hum, 0.07, 5.6, 0.4, 0.1, [], 0.5, 10.45),
         (rain, 0.14, 0.0, 1.0, 0.6, [], 0, 9.0), (rain, 0.14, 8.4, 0.6, 1.0, [], 0.5, 15.0),
         (U + "music/ub_system_puls.mp3", 0.45, 0.0, 0.6, 0.2, [], 30.0, 5.95),
         (U + "music/ub_ausfall_dunkel.mp3", 0.32, 8.0, 1.5, 1.0, [(12.2, -10, 0.5)], 10.0, 15.0)]
print(mix("/home/claude/stilproben/stilprobe_unterbau.mp4", "/home/claude/stilproben/ton_unterbau.mp4", ev, 15.0, music))
