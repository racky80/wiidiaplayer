#!/bin/bash

FPS=16
nice -n 1 ffmpeg -y -i "$1" -ar 44100 -ab 128k -b 400k -r $FPS -f flv -s 400x224 -ac 1 "$2" 2>&1