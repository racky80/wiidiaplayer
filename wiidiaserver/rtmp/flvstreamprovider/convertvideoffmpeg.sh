#!/bin/bash
function getffmpegchildids {
	ps --ppid $$ | awk '$4=="ffmpeg" {print $1}'
}

function stop_encoding {
	echo $$ > /tmp/proc_$$
	echo
	echo "now stopping"
	echo
	echo
	PIDS="$(getffmpegchildids)"
	for mypid in $PIDS; do
		kill $mypid > /dev/null 2>&1;
	done
	sleep 2;
	PIDS="$(getffmpegchildids)"
	for mypid in $PIDS; do
		kill -9 $mypid > /dev/null 2>&1;
	done
}
trap stop_encoding TERM;
trap stop_encoding EXIT;

FPS=16
nice -n 1 ffmpeg -y -i "$1" -ar 44100 -ab 128k -b 400k -r $FPS -f flv -s 400x224 -ac 1 "$2" 2>&1 &

sleep 5

while [ -n "$(getffmpegchildids)" ]; do
	sleep 1;
done
