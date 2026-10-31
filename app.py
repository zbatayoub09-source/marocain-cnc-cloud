import os, re, time
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify, render_template, request, send_from_directory
from designer import make_spec
from engine import generate, build_svg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
os.makedirs(OUT, exist_ok=True)
app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def api_generate():
    word = ((request.get_json(silent=True) or {}).get("word") or "").strip()[:40]
    if not word:
        return jsonify(error="Type a word first."), 400
    spec = make_spec(word)
    svg = build_svg(generate(spec), spec["title"] or word)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", word).strip("_") or "design"
    name = f"{slug}_{spec['motif']}_{int(time.time())}.svg"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    return jsonify(file=name, svg=svg, spec=spec, word=word)


@app.get("/download/<name>")
def download(name):
    return send_from_directory(OUT, name, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
