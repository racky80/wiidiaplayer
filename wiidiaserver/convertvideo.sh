#!/bin/bash

i=0;
while [ -e "/tmp/convertvideo_fifo_$i" ]; do
	i=$(($i+1))
done
fifo="/tmp/convertvideo_fifo_$i"
mkfifo "$fifo";
/usr/bin/mencoder "$1"  -af resample=44100:0:1 -msglevel all=-1:mencoder=4 -of lavf -lavfopts  format=flv:i_certify_that_my_video_stream_does_not_use_b_frames -af resample=44100:0:1 -af channels=2 -oac mp3lame -lameopts cbr:br=192 -ovc lavc -lavcopts vcodec=flv:vbitrate=500:autoaspect:vratetol=4:keyint=25 -mc 0 -o "$fifo" >/dev/null &
cat "$fifo"
unlink "$fifo"
