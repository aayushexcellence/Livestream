from flask import (
    Blueprint, g, request, abort, jsonify
)
import requests
from app import mongo
import json
import time
import psutil
import ffmpeg

bp = Blueprint('ffmpeg', __name__, url_prefix='/ffmpeg')


@bp.route('/livestream', methods=['GET'])
def livestream():
    state = request.args.get("state")
    subdomain = request.args.get("subdomain")
    if state:
        subdomain = mongo.db.ffmpeg.find_one({"subdomain":subdomain})
        pid = subdomain['pid']
        process = psutil.Process(int(pid))
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
    else:
        RTMP_PATH = "rtmp://127.0.0.1:1935/live/"+subdomain
        process = (
            ffmpeg 
            .input('https://images.platoo.in/video/glassblower_glass_heat_glowing_hot_354.mp43d437149303e467883155300b76a4f3e.mp4',stream_loop="-1")
            .output(
            RTMP_PATH,
            f='flv',
            vcodec='h264',
            preset='ultrafast',
            acodec='aac')
            .global_args("-re")
            .global_args("-nostdin") 
            .overwrite_output()
        )
        process = process.run_async(pipe_stdin=True)
        is_subdomain = mongo.db.ffmpeg.update({"subdomain":subdomain},{"$set":{"pid":process.pid}},upsert=True)
    return jsonify({"status":"successfully runing"})
   
