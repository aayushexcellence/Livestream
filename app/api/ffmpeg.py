from flask import (
    Blueprint, g, request, abort, jsonify
)
import requests
from app import mongo
import json
import time
import psutil
import io
import os
import subprocess

bp = Blueprint('ffmpeg', __name__, url_prefix='/')


Rmtp_json = {
    "youtube":"rtmp://a.rtmp.youtube.com/live2/xuzk-dc7m-9zc3-zy0k-8wck",
    "twitch":"rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ",
    "facebook":"rtmps://live-api-s.facebook.com:443/rtmp/1412237025777635?s_bl=1&s_ps=1&s_psm=1&s_sw=0&s_vt=api-s&a=AbzVxXXUA44qNyEy",
    "vimeo":"rtmps://rtmp-global.cloud.vimeo.com:443/live/037fe25f-9fa2-4829-a61c-3963f3d395c9"
}

@bp.route('/livestream', methods=['GET'])
def livestream():
    state = request.args.get("state")
    pid = request.args.get("pid")
    platform = request.args.get("platform")
    subdomain = request.args.get("subdomain")
    audio_port = request.args.get("audio_port")
    video_port = request.args.get("video_port")
    host = request.args.get("host")
    if host is None:
        host = "127.0.0.1"
    dir_path = os.path.dirname(os.path.realpath(__file__))
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
        if pid is None:
            if platform == "youtube":
                RTMP_PATH = "rtmp://a.rtmp.youtube.com/live2/xuzk-dc7m-9zc3-zy0k-8wck"
            elif platform == "twitch":
                RTMP_PATH = "rtmp://bom01.contribute.live-video.net/app/live_656490184_THjxxhho7zir5R6Rh9xoK3JnSdZiNJ"
            elif platform == "facebook":
                RTMP_PATH = "rtmps://live-api-s.facebook.com:443/rtmp/1418625858472085?s_bl=1&s_psm=1&s_sc=1418625885138749&s_sw=0&s_vt=api-s&a=Abx0I9C5X7H_iUyk"
            elif platform == "vimeo":
                RTMP_PATH = "rtmps://rtmp-global.cloud.vimeo.com:443/live/037fe25f-9fa2-4829-a61c-3963f3d395c9"
            else:
                RTMP_PATH = "rtmp://127.0.0.1:1935/live/"+subdomain
            writesdp(subdomain,audio_port,video_port,host)
            command = "ffmpeg -protocol_whitelist file,rtp,udp,https,tls,tcp -i "+str(dir_path)+"/janus/"+str(subdomain)+".sdp -c:v libx264 -c:a aac -ar 16k -ac 1 -preset ultrafast -tune zerolatency -f flv "+str(RTMP_PATH)+" 2> "+str(dir_path)+"/logs/"+str(subdomain)+".log"
            process = subprocess.Popen(command,shell=True)        
            is_subdomain = mongo.db.ffmpeg.update({"subdomain":subdomain},{"$set":{"pid":process.pid}},upsert=True)
            time.sleep(10)
            with open(str(dir_path)+"/logs/"+str(subdomain)+".log") as file: 
                for line in (file.readlines() [:500]): 
                    if "bind failed: Address already in use" in line:
                        return jsonify({"status":"bind failed: Address already in use"})
        else:
            try:
                platform_list = platform.split(",")
                try:
                    process = psutil.Process(int(pid))
                    for proc in process.children(recursive=True):
                        proc.kill()
                    process.kill()
                except Exception:
                    pass
                if len(platform_list) == 2:
                    command = "ffmpeg -protocol_whitelist file,rtp,udp,https,tls,tcp -i "+str(dir_path)+"/janus/"+str(subdomain)+".sdp -c copy -c:a aac -ar 16k -ac 1 -vcodec h264 -preset ultrafast -tune zerolatency -f flv "+str(Rmtp_json[platform_list[0]])+" -c:v libx264 -c:a aac -ar 16k -ac 1 -preset ultrafast -tune zerolatency -f flv "+str(Rmtp_json[platform_list[1]])+" 2> "+str(dir_path)+"/logs/"+str(subdomain)+".log"
                if len(platform_list) == 3:
                    command = "ffmpeg -protocol_whitelist file,rtp,udp,https,tls,tcp -1 -i "+str(dir_path)+"/janus/"+str(subdomain)+".sdp -c:v libx264 -c:a aac -ar 16k -ac 1 -preset ultrafast -tune zerolatency -f flv "+str(RTMP_PATH)+" 2> "+str(dir_path)+"/logs/"+str(subdomain)+".log"
                writesdp(subdomain,audio_port,video_port,host)
                process = subprocess.Popen(command,shell=True)        
                is_subdomain = mongo.db.ffmpeg.update({"subdomain":subdomain},{"$set":{"pid":process.pid}},upsert=True)
                time.sleep(10)
                with open(str(dir_path)+"/logs/"+str(subdomain)+".log") as file: 
                    for line in (file.readlines() [:500]): 
                        if "bind failed: Address already in use" in line:
                            return jsonify({"status":"bind failed: Address already in use"})
            except Exception as e:
                return jsonify({"status":"err","error":str(e)})            
    return jsonify({"status":"successfully running","pid":process.pid})
   



def writesdp(subdomain,audio_port,video_port,host):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    save_path = str(dir_path)+"/janus/"
    file_name = subdomain+".sdp"
    completeName = os.path.join(save_path, file_name)
    
    default_file = open(dir_path+"/janus.sdp" , "r")
    
    file1 = open(completeName, "w")

    for line in default_file:
    #write that line to the new file
        if "AUDIOPORT" in line:
            replaced_line = line.replace("AUDIOPORT",''+str(audio_port)+'')
        elif "VIDEOPORT" in line:
            replaced_line = line.replace("VIDEOPORT",''+str(video_port)+'')
        elif "HOST" in line:
            replaced_line = line.replace("HOST",''+str(host)+'')
        else:
            replaced_line = line
        file1.write(replaced_line)
    file1.close()
    return True


def check_pid(pid):        
    """ Check For the existence of a unix pid. """
    try:
        os.kill(int(pid), 0)
    except OSError:
        return False
    else:
        return True



@bp.route('/checklogs', methods=['GET'])
def checklogs():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    subdomain = request.args.get("subdomain")
    pid = request.args.get("pid")
    pidstatus = check_pid(pid)
    logs_dict = {}
    with open(str(dir_path)+"/logs/"+str(subdomain)+".log") as file: 
        count = 0
        for line in (file.readlines() [-1000:]): 
            logs_dict[str(count)] = line
            count = count+1
    return jsonify({"is_pid_running":pidstatus,"Logs":logs_dict})


