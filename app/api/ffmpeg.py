from flask import (
    Blueprint, g, request, abort, jsonify
)
import requests
from app import mongo
import json
import time
import psutil
import ffmpeg

bp = Blueprint('ffmpeg', __name__, url_prefix='/')


@bp.route('/livestream', methods=['GET'])
def livestream():
    state = request.args.get("state")
    platform = request.args.get("platform")
    subdomain = request.args.get("subdomain")
    if state:
        if state == "off":
            try:
                subdomain = mongo.db.ffmpeg.find_one({"subdomain":subdomain})
                pid = subdomain['pid']
                process = psutil.Process(int(pid))
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
            except Exception:
                pass
            return jsonify({"status":"stopped"})
    else:
        if platform == "youtube":
            RTMP_PATH = "rtmp://a.rtmp.youtube.com/live2/xuzk-dc7m-9zc3-zy0k-8wck"
        elif platform == "twitch":
            RTMP_PATH = "rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ"
        elif platform == "facebook":
            RTMP_PATH = "rtmps://live-api-s.facebook.com:443/rtmp/1412237025777635?s_bl=1&s_ps=1&s_psm=1&s_sw=0&s_vt=api-s&a=AbzVxXXUA44qNyEy"
        else:
            RTMP_PATH = "rtmp://127.0.0.1:1935/live/"+subdomain
        
        process = (
            ffmpeg 
            .input('/root/Project1/Livestream/janus.sdp',stream_loop="-1",protocol_whitelist="rtmp,rtmps,tls,tcp,https,file,rtp,udp")
            .output(
            RTMP_PATH,
            f='flv',
            vcodec='h264',
            preset='ultrafast',
            acodec='aac',
            tune="zerolatency")
            .global_args("-re")
            .global_args("-nostdin") 
            .overwrite_output()
        )
        process = process.run_async()
        is_subdomain = mongo.db.ffmpeg.update({"subdomain":subdomain},{"$set":{"pid":process.pid}},upsert=True)
    return jsonify({"status":"successfully running"})
   
