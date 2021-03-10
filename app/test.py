"""
import json
import time
import psutil
import ffmpeg
ffmpeg -protocol_whitelist file,rtp,udp  -i janus.sdp -c:v h264 -preset:v ultrafast -acodec aac -tune zerolatency -f flv rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ
ffmpeg -protocol_whitelist file,rtp,udp -i janus.sdp -c:v h264 -preset:v ultrafast -acodec aac -tune zerolatency -f flv rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ


RTMP_PATH = "rtmp://127.0.0.1:1935/live/livestream"#"rtmp://127.0.0.1:1935/live/"+subdomain


process = (
    ffmpeg 
    .input('https://images.platoo.in/video/glassblower_glass_heat_glowing_hot_354.mp43d437149303e467883155300b76a4f3e.mp4',stream_loop="-1")
    .output(
    RTMP_PATH,
    f='flv',
    vcodec='h264',
    preset='ultrafast',
    acodec='aac',
    tune="zerolatency",
    protocol_whitelist="rtmp,rtmps,tls,tcp,file,rtp,udp")
    .global_args("-re")
    .global_args("-nostdin") 
    .overwrite_output()
)

process = process.run_async(pipe_stdin=False)
"""
"""
import cv2
cap = cv2.VideoCapture("rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ")

while(cap.isOpened()):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
"""
import cv2
myrtmp_addr = "rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ"
cap = cv2.VideoCapture(myrtmp_addr)
frame,err = cap.read()