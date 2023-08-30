#!/bin/bash
pactl set-sink-mute @DEFAULT_SINK@ false
pactl set-sink-volume @DEFAULT_SINK@ 100%
curl https://www.google.com/speech-api/v1/synthesize\?text\=$1\&lang\=it\&client\=lr-language-tts --output .voice &&  cvlc .voice vlc://quit && rm .voice
