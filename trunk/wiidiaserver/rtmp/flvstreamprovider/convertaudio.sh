#!/bin/bash

function stop_encoding {
	firstcoderpid=$!
	echo "Now killing children $firstcoderpid"
	kill $firstcoderpid
}
trap stop_encoding EXIT;

ffmpeg -re -v 0 -y -i "$1" -async 1 -ar 44100 -ab 320k -f flv "$2"


