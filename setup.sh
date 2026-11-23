#!/bin/sh
# Usage: sh setup.sh videos/NNN-slug /home/claude/unterbau-work
# Legt den Arbeitsordner an (audio/, img/, words/, music/, sfx/) und lädt alles Kostenlose:
#   Tiefenmodell (2.5D), Parakeet-Spracherkennung (Wortzeiten), eigene Unterbau-Sounds + Musik.
set -e
REPO=$(cd "$(dirname "$0")" && pwd); VID="$REPO/$1"; WORK="${2:-/home/claude/unterbau-work}"
mkdir -p "$WORK/audio" "$WORK/img" "$WORK/words" "$WORK/music" "$WORK/sfx" /home/claude/models
pip install onnxruntime sherpa-onnx --break-system-packages -q 2>/dev/null || true
[ -f /home/claude/models/da2s.onnx ] || curl -sSfL -o /home/claude/models/da2s.onnx https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model.onnx
if [ ! -d /home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 ]; then
  curl -sSfL -o /tmp/parakeet.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2
  tar xjf /tmp/parakeet.tar.bz2 -C /home/claude/models && rm /tmp/parakeet.tar.bz2
fi
# Unterbau hat eigene Effekte (assets/sfx) – die Goldsmith-Bibliothek wird nicht eingebunden (Laurin 17.11.2026: jeder Kanal eigene Effekte)
cp "$REPO"/assets/sfx/*.* "$WORK/sfx/" 2>/dev/null || true
cp "$REPO"/assets/music/*.mp3 "$WORK/music/" 2>/dev/null || true
[ -f "$VID/spec.json" ] && cp "$VID/spec.json" "$WORK/"
# Ton-Werkzeug audiokit (18.11.2026): Sounds aufräumen, Musik nach Spannungskurve, Endkontrolle.
# Gemeinsam sind nur die Regeln – Sounds und Musik bleiben kanal-eigen. Repo: laurindesruelles-max/sound-mediathek
AK="${AUDIOKIT:-/home/claude/audiokit}"
if [ ! -f "$AK/adapter.py" ] || [ -n "$AK_UPDATE" ]; then
  AKT=$(mktemp -d); git clone -q --depth 1 --filter=blob:none --sparse https://github.com/laurindesruelles-max/sound-mediathek "$AKT/r" && git -C "$AKT/r" sparse-checkout set audiokit && mkdir -p "$AK" && cp "$AKT"/r/audiokit/*.py "$AKT"/r/audiokit/*.json "$AK"/ && echo "audiokit bereit: $AK"; rm -rf "$AKT"
fi
# Laurins Sound-Bibliothek (19.11.2026): eigene Effekte dieses Kanals + gemeinsame Geräusche -> /home/claude/sfx-bibliothek/bibliothek
python3 -c "import sys; sys.path.insert(0, '$AK'); import bibliothek; print('Sound-Bibliothek bereit:', bibliothek.ensure('unterbau'))" || echo "WARNUNG: Sound-Bibliothek nicht geladen"
echo "Arbeitsordner bereit: $WORK  (Stimme -> audio/, Bilder -> img/NN.png, dann words/ mit engine/wordtimes.py)"

# 2D-Motion-Graphics (Remotion): Node-Pakete einmal installieren
[ -d "$(dirname "$0")/engine/motion2d/node_modules" ] || (cd "$(dirname "$0")/engine/motion2d" && npm install --silent >/dev/null 2>&1 && echo "motion2d bereit")
