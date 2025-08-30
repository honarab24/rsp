import subprocess, os, threading, time
from flask import Flask, send_from_directory, jsonify

app = Flask(__name__)
HLS_DIR = "/tmp/hls"
os.makedirs(HLS_DIR, exist_ok=True)

# MPD source
MPD_URL = "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/celmovie_pinoy_sd.mpd"

# Clearkey DRM
KID = "0f8537d8412b11edb8780242ac120002"
KEY = "2ffd7230416150fd5196fd7ea71c36f3"

# Try with KEY only first (if KID:KEY fails)
CLEARKEY = KEY
# CLEARKEY = f"{KID}:{KEY}"   # enable this if ffmpeg requires KID:KEY

def run_ffmpeg():
    while True:
        print("🚀 Starting ffmpeg...", flush=True)
        process = subprocess.Popen([
            "ffmpeg", "-y",
            "-decryption_key", CLEARKEY,
            "-i", MPD_URL,
            "-c:v", "copy", "-c:a", "copy",
            "-f", "hls",
            "-hls_time", "6",
            "-hls_list_size", "10",
            "-hls_flags", "delete_segments+append_list+omit_endlist",
            os.path.join(HLS_DIR, "celestial.m3u8")
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in iter(process.stdout.readline, b''):
            print(line.decode().strip(), flush=True)

        process.wait()
        print("⚠️ ffmpeg exited. Restarting in 5s...", flush=True)
        time.sleep(5)

# Run ffmpeg in background
threading.Thread(target=run_ffmpeg, daemon=True).start()

@app.route("/<path:filename>")
def serve_file(filename):
    return send_from_directory(HLS_DIR, filename)

@app.route("/")
def index():
    return "Restream is running. Playlist: /celestial.m3u8"

@app.route("/healthz")
def healthz():
    if os.path.exists(os.path.join(HLS_DIR, "celestial.m3u8")):
        return jsonify(status="ok"), 200
    else:
        return jsonify(status="starting"), 503

@app.route("/debug")
def debug():
    return {"files": os.listdir(HLS_DIR)}
