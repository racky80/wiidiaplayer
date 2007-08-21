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

FPS=13

/usr/bin/mencoder "$1" \
				-of lavf -lavfopts format=asf:i_certify_that_my_video_stream_does_not_use_b_frames \
                -oac pcm -ovc raw \
                -vf scale=320:240 -af resample=44100:0:1 -ofps $FPS \
                -o /dev/fd/3 3>&1 >/dev/null 2&>1 | \
       /usr/bin/mencoder /dev/stdin \
				-of lavf -lavfopts  format=flv:i_certify_that_my_video_stream_does_not_use_b_frames \
                -af resample=44100:0:1 -af channels=2 -oac mp3lame -lameopts cbr:br=192 -mc 0 \
                -ovc lavc -lavcopts vcodec=flv:vbitrate=2500:autoaspect:vratetol=4:keyint=25 -ofps $FPS -o "$2" > /dev/null 2&>1 &
while [ -n "$(getmencoderchildids)" ]; do
	sleep 1;
done
