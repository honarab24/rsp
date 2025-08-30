from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# Common headers for IPTV servers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.35/36 Safari/537.36",
    "Referer": "https://jxoxkplay.xyz/",
    "Origin": "https://jxoxkplay.xyz"
}

def fetch_url(url, extra_headers=None, stream=False):
    headers = DEFAULT_HEADERS.copy()
    if extra_headers:
        headers.update(extra_headers)
    return requests.get(url, headers=headers, stream=stream, timeout=15)


@app.route("/proxy/m3u")
def proxy_m3u():
    url = request.args.get("url")
    if not url:
        return "Missing url param", 400

    resp = fetch_url(url)
    if resp.status_code != 200:
        return f"Failed to fetch {url} (status {resp.status_code})", 502

    # Rewrite playlist so .ts and .key go back through proxy
    base_url = url.rsplit("/", 1)[0]
    lines = []
    for line in resp.text.splitlines():
        if line.strip().startswith("#"):
            lines.append(line)
        elif line.strip():
            if not line.startswith("http"):
                proxied = f"{base_url}/{line}"
            else:
                proxied = line
            lines.append(f"/proxy/ts?url={proxied}")
    return Response("\n".join(lines), mimetype="application/vnd.apple.mpegurl")


@app.route("/proxy/ts")
def proxy_ts():
    url = request.args.get("url")
    if not url:
        return "Missing url param", 400

    r = fetch_url(url, stream=True)
    return Response(r.iter_content(chunk_size=8192),
                    content_type=r.headers.get("content-type", "video/MP2T"))


@app.route("/")
def home():
    return "✅ Proxy server is running!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Render gives $PORT
    app.run(host="0.0.0.0", port=port)
