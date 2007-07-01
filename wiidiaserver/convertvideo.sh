#!/bin/bash

i=0;
while [ -e "/tmp/convertvideo_fifo_$i" -o -e "/tmp/convertvideo_fifo_2_$i" ]; do
	i=$(($i+1))
done
fifo="/tmp/convertvideo_fifo_$i"
fifo2="/tmp/convertvideo_fifo_2_$i"
mkfifo "$fifo";
mkfifo "$fifo2";
/usr/bin/mencoder "$1" -af resample=44100:0:1 -oac pcm -ovc lavc -lavcopts vcodec=mjpeg:vqscale=0 -vf scale=320:180 -o "$fifo2" >/dev/null &
/usr/bin/mencoder "$fifo2" -of lavf -lavfopts  format=flv:i_certify_that_my_video_stream_does_not_use_b_frames -af resample=44100:0:1 -af channels=2 -oac mp3lame -lameopts cbr:br=192 -ovc lavc -lavcopts vcodec=flv:vbitrate=10000:autoaspect:vratetol=4:keyint=25 -mc 0 -o "$fifo" >/dev/null &
cat "$fifo"
unlink "$fifo"
unlink "$fifo2"
