# stsmedserv
Stupidly simple media server


Convering: 

For webm (VP8 / Vorbis):
ffmpeg -i S01E01_Pups.avi -vcodec libvpx -acodec libvorbis -f webm -g 30 S01E01_Pups-FF4.avi

