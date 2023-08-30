#!/bin/bash
pactl set-sink-mute @DEFAULT_SINK@ false
pactl set-sink-volume @DEFAULT_SINK@ 50%
var=$(echo "$1" | sed 's/\ /%20/g' )
echo https://www.google.com/speech-api/v1/synthesize\?text\=$var\&lang\=it\&client\=lr-language-tts
curl https://www.google.com/speech-api/v1/synthesize\?text\=$var\&lang\=it\&client\=lr-language-tts --output .voice && cvlc .voice vlc://quit
rm -f .voice
