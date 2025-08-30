from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

# Default headers to mimic a real browser/player
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Referer": "https://newkso.ru/",
    "Origin": "https://newkso.ru",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def fetch_url(url, stream=False):
    """Fetch a URL with IPTV-friendly headers"""
    try:
        return requests.get(url, headers=DEFAULT_HEADERS, stream=stream, timeout=15)
    except Exception as e:
        return None


@app.route("/proxy/m3u")
def proxy_m3u():
    url = request.args.get("url")
    if not url:
        return "❌ Missing url param", 400

    resp = fetch_url(url)
    if resp is None:
        return "❌ Error fetching URL", 502
    if resp.status_code != 200:
        return f"❌ Failed to fetch {url} (status {resp.status_code})", 502

    base_url = url.rsplit("/", 1)[0]
    lines = []

    for line in resp.text.splitlines():
        if line.strip().startswith("#") or not line.strip():
            # Keep comments/metadata as-is
            lines.append(line)
        else:
            # Rewrite relative or absolute URLs to go through proxy
            if not line.startswith("http"):
                target = f"{base_url}/{line}"
            else:
                target = line

            if target.endswith(".ts"):
                proxied = f"/proxy/ts?url={target}"
            elif target.endswith(".key"):
                proxied = f"/proxy/key?url={target}"
            else:
                proxied = f"/proxy/m3u?url={target}"

            lines.append(proxied)

    return Response("\n".join(lines), mimetype="application/vnd.apple.mpegurl")


@app.route("/proxy/ts")
def proxy_ts():
    url = request.args.get("url")
    if not url:
        return "❌ Missing url param", 400

    r = fetch_url(url, stream=True)
    if r is None:
        return "❌ Error fetching .ts", 502

    return Response(r.iter_content(chunk_size=8192),
                    content_type=r.headers.get("content-type", "video/MP2T"))


@app.route("/proxy/key")
def proxy_key():
    url = request.args.get("url")
    if not url:
        return "❌ Missing url param", 400

    r = fetch_url(url, stream=True)
    if r is None or r.status_code != 200:
        return "❌ Failed to fetch key", 502

    return Response(r.content, content_type="application/octet-stream")


@app.route("/")
def home():
    return "✅ Proxy server is running!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Render gives a dynamic $PORT
    app.run(host="0.0.0.0", port=port)
