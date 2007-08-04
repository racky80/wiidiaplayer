#!/bin/bash

function stop_encoding {
	secondcoderpid=$!
	echo "Now killing children $firstcoderpid and $secondcoderpid"
	kill $firstcoderpid
	kill $secondcoderpid
	unlink "$fifo"
}
trap stop_encoding EXIT;

i=0;
while [ -e "/tmp/convertvideo_fifo_$i" -o -e "/tmp/convertvideo_fifo_2_$i" ]; do
	i=$(($i+1))
done
fifo="/tmp/convertvideo_fifo_$i"
fifo2="/tmp/convertvideo_fifo_2_$i"
mkfifo "$fifo";
/usr/bin/mencoder "$1" -vf scale=320:240 -af resample=44100:0:1 -oac pcm -ovc raw -ofps 15 -o "$fifo" > /dev/null&
firstcoderpid=$!
/usr/bin/mencoder "$fifo" -of lavf -lavfopts  format=flv:i_certify_that_my_video_stream_does_not_use_b_frames -af resample=44100:0:1 -af channels=2 -oac mp3lame -lameopts cbr:br=192 -ovc lavc -lavcopts vcodec=flv:vbitrate=2500:autoaspect:vratetol=4:keyint=25 -mc 0 -o "$2" > /dev/null
unlink "$fifo"
