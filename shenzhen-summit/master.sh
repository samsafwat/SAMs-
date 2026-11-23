#!/bin/sh
# ffmpeg 6 fallback for mux.sh: two-pass loudnorm to -14 LUFS / -1 dBTP, then mux with the picture.
set -e
V=$1; A=$2; O=$3
J=$(ffmpeg -hide_banner -nostats -i "$A" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -hide_banner -y -loglevel error -i "$A" -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -c:a pcm_s16le "${O%.mp4}.master.wav"
ffmpeg -hide_banner -y -loglevel error -i "$V" -i "${O%.mp4}.master.wav" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart "$O"
rm -f "${O%.mp4}.master.wav"
