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
echo "Arbeitsordner bereit: $WORK  (Stimme -> audio/, Bilder -> img/NN.png, dann words/ mit engine/wordtimes.py)"
