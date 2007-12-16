#!/bin/bash
/usr/bin/mplayer "$1" -identify -frames 0 -vo null -ao null 2>/dev/null | awk 'BEGIN {FS="="} $1=="ID_VIDEO_CODEC" {print $2}'