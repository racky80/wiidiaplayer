#!/bin/bash

function getmencoderchildids {
	ps --ppid $$ | awk '$4=="mencoder" {print $1}'
}

function stop_encoding {
	echo "now stopping"
	PIDS="$(getmencoderchildids)"
	for mypid in $PIDS; do
		kill $mypid > /dev/null 2&>1;
	done
	sleep 2;
	PIDS="$(getmencoderchildids)"
	for mypid in $PIDS; do
		kill -9 $mypid > /dev/null 2&>1;
	done
}
trap stop_encoding TERM;
trap stop_encoding EXIT;

FPS=17
nice -n 2 /usr/bin/mencoder "$1" \
				-of lavf -lavfopts format=asf \
                -oac pcm -af resample=44100:0:1 \
                -ovc raw -vf scale=400:224 \
                -o /dev/fd/3 3>&1 >/var/log/mencoder/1 2>&1 | \
        nice -n 1 /usr/bin/mencoder /dev/stdin \
        		-of lavf -lavfopts format=flv \
        		-af resample=44100:0:1 -af channels=2 -oac mp3lame -lameopts cbr:br=128 -mc 0 \
        		-ovc lavc -lavcopts vcodec=flv:vbitrate=2500:autoaspect:vratetol=1000:keyint=1 -ofps $FPS \
        		-o "$2" > /var/log/mencoder/2 2>&1 &


while [ -n "$(getmencoderchildids)" ]; do
	sleep 1;
done
