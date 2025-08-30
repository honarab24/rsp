from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400
    headers = {
        "Origin": "https://qp-pldt-live-grp-01-prod.akamaized.net",
        "Referer": "https://qp-pldt-live-grp-01-prod.akamaized.net/"
    }
    r = requests.get(url, headers=headers, stream=True)
    return Response(r.iter_content(chunk_size=8192),
                    status=r.status_code,
                    content_type=r.headers.get("Content-Type"))
