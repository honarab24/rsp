import subprocess, os
from flask import Flask, send_from_directory

app = Flask(__name__)
HLS_DIR = "/tmp/hls"
os.makedirs(HLS_DIR, exist_ok=True)

# Start ffmpeg conversion (DASH -> HLS)
subprocess.Popen([
    "ffmpeg", "-y",
    "-i", "https://qp-pldt-live-grp-01-prod.akamaized.net/out/u/celmovie_pinoy_sd.mpd",
    "-c", "copy",
    "-f", "hls",
    "-hls_time", "6",
    "-hls_list_size", "10",
    "-hls_flags", "delete_segments",
    os.path.join(HLS_DIR, "celestial.m3u8")
])

@app.route("/celestial.m3u8")
def playlist():
    return send_from_directory(HLS_DIR, "celestial.m3u8")

@app.route("/<path:path>")
def serve_file(path):
    return send_from_directory(HLS_DIR, path)
