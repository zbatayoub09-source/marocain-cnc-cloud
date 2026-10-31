"""Turns one word into a design spec. Uses Claude if a key is set, else a built-in dictionary."""
import json, os, re

KEYWORDS = {
    "biban": {"motif": "rosette", "n": 12},
    "zellij": {"motif": "zellij", "grid": 4, "n": 8},
    "zellige": {"motif": "zellij", "grid": 4, "n": 8},
    "warda": {"motif": "warda", "rings": 3, "n": 6},
    "korsi": {"motif": "rosette", "n": 8, "frame": "square"},
    "bab": {"motif": "arch", "n": 8},
}

SYSTEM = """You design Moroccan CNC ornaments. The user gives one word (Moroccan Arabic, Arabic, French or English).
Pick the motif that best fits its meaning and reply with JSON ONLY, no markdown:
{"motif":"zellij|rosette|warda|arch","title":"short name","meaning":"one short sentence",
 "n":int,"grid":int,"rings":int,"frame":"circle|square"}
motif: zellij = tiled star-and-diamond mosaic (n 6-12 star points, grid 3-6);
rosette = radial geometric star medallion (n 6-16 points; frame circle or square);
warda = layered rose/flower (n 5-8 petals in first ring, rings 2-4);
arch = horseshoe door/arch/window with star and leaves (n 6-12).
Vary the numbers a little so repeated words give different designs."""


def clean(s):
    clamp = lambda v, lo, hi, d: max(lo, min(hi, int(v))) if str(v).lstrip("-").isdigit() else d
    m = s.get("motif") if s.get("motif") in ("zellij", "rosette", "warda", "arch") else "rosette"
    return {"motif": m, "title": str(s.get("title", ""))[:60], "meaning": str(s.get("meaning", ""))[:160],
            "n": clamp(s.get("n", 8), 5, 16, 8), "grid": clamp(s.get("grid", 4), 3, 6, 4),
            "rings": clamp(s.get("rings", 3), 2, 4, 3),
            "frame": s.get("frame") if s.get("frame") in ("circle", "square") else "circle"}


def make_spec(word):
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key:
        try:
            import anthropic
            msg = anthropic.Anthropic(api_key=key).messages.create(
                model=os.getenv("MODEL", "claude-sonnet-5-5"), max_tokens=300, system=SYSTEM,
                messages=[{"role": "user", "content": word}])
            text = "".join(b.text for b in msg.content if b.type == "text")
            spec = clean(json.loads(re.search(r"\{.*\}", text, re.S).group(0)))
            spec["source"] = "AI"
            return spec
        except Exception as e:
            print("AI call failed, using fallback:", e)
    base = KEYWORDS.get(word.lower())
    if not base:
        h = sum(map(ord, word.lower()))
        base = [KEYWORDS["biban"], KEYWORDS["zellij"], KEYWORDS["warda"], KEYWORDS["bab"]][h % 4]
    spec = clean({**base, "title": word, "meaning": "Offline mode: add an API key for AI understanding."})
    spec["source"] = "offline"
    return spec
