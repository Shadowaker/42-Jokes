#!/bin/bash
pactl set-sink-mute @DEFAULT_SINK@ false
pactl set-sink-volume @DEFAULT_SINK@ 100%
var=$(echo "$1" | sed 's/\ /%20/g' )
curl https://www.google.com/speech-api/v1/synthesize\?text\=$var\&lang\=it\&client\=lr-language-tts --output .voice >/dev/null 2>&1
cvlc .voice vlc://quit >/dev/null 2>&1
rm -f .voice
