"""Geometry engine: builds closed, non-overlapping vector paths (units = mm)."""
import math
from xml.sax.saxutils import escape

S = 300.0  # canvas size in mm


def P(cx, cy, r, a):
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def poly(pts):
    return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"


def star(cx, cy, n, ro, ri, rot=-math.pi / 2):
    return poly([P(cx, cy, ro if i % 2 == 0 else ri, rot + i * math.pi / n) for i in range(2 * n)])


def circle(cx, cy, r):
    return (f"M{cx - r:.3f},{cy:.3f} A{r:.3f},{r:.3f} 0 1 0 {cx + r:.3f},{cy:.3f} "
            f"A{r:.3f},{r:.3f} 0 1 0 {cx - r:.3f},{cy:.3f} Z")


def rect(x, y, w, h):
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def frame(kind, m=8, t=7):
    c = S / 2
    if kind == "circle":
        return [circle(c, c, c - m) + " " + circle(c, c, c - m - t)]
    k = m + t
    return [rect(m, m, S - 2 * m, S - 2 * m) + " " + rect(k, k, S - 2 * k, S - 2 * k)]


def petal(cx, cy, r0, L, w, a):
    ca, sa = math.cos(a), math.sin(a)

    def T(x, y):
        return (cx + (r0 + x) * ca - y * sa, cy + (r0 + x) * sa + y * ca)

    p = [T(0, 0), T(.25 * L, -w), T(.8 * L, -w), T(L, 0), T(.8 * L, w), T(.25 * L, w)]
    f = lambda q: f"{q[0]:.3f},{q[1]:.3f}"
    return f"M{f(p[0])} C{f(p[1])} {f(p[2])} {f(p[3])} C{f(p[4])} {f(p[5])} {f(p[0])} Z"


def zellij(spec):
    c = int(spec.get("grid", 4)); n = int(spec.get("n", 8))
    x0 = 22; s = (S - 2 * x0) / c
    out = frame("square")
    for i in range(c):
        for j in range(c):
            cx, cy = x0 + (i + .5) * s, x0 + (j + .5) * s
            out.append(star(cx, cy, n, .44 * s, .26 * s) + " " + circle(cx, cy, .07 * s))
    d = .17 * s
    for i in range(1, c):
        for j in range(1, c):
            cx, cy = x0 + i * s, x0 + j * s
            out.append(poly([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]))
    return out


def rosette(spec):
    n = int(spec.get("n", 12)); c = S / 2
    out = frame(spec.get("frame", "circle"))
    out.append(star(c, c, n, 46, 46 * .62) + " " + circle(c, c, 9))
    d = math.pi / n * .62
    for i in range(n):
        a = -math.pi / 2 + i * 2 * math.pi / n
        out.append(poly([P(c, c, 54, a), P(c, c, 72, a + d), P(c, c, 102, a), P(c, c, 72, a - d)]))
        b = a + math.pi / n
        x, y = P(c, c, 122, b)
        out.append(star(x, y, 4, 10, 4, b))
    return out


def warda(spec):
    rings = int(spec.get("rings", 3)); n0 = int(spec.get("n", 6)); c = S / 2
    out = frame(spec.get("frame", "circle"))
    out.append(circle(c, c, 12))
    gap = 5; r = 18; L = (124 - 18 - gap * (rings - 1)) / rings
    for k in range(rings):
        n = n0 * (k + 1)
        w = 3.3 * (r + L / 2) / n
        for i in range(n):
            a = -math.pi / 2 + k * math.pi / n + i * 2 * math.pi / n
            out.append(petal(c, c, r, L, w, a))
        r += L + gap
    return out


def arch(spec):
    cx = S / 2; W = 190; t = 14; base = S - 14; n = int(spec.get("n", 8))

    def horseshoe(w, ysp, r, yb):
        x0, x1 = cx - w / 2, cx + w / 2
        return (f"M{x0:.3f},{yb:.3f} L{x0:.3f},{ysp:.3f} A{r:.3f},{r:.3f} 0 1 1 "
                f"{x1:.3f},{ysp:.3f} L{x1:.3f},{yb:.3f} Z")

    r = W * .56; ysp = 175; cy = ysp - math.sqrt(r * r - (W / 2) ** 2)
    ri = r - t; wi = W - 2 * t
    ysp_i = cy + math.sqrt(ri * ri - (wi / 2) ** 2)
    out = [horseshoe(W, ysp, r, base) + " " + horseshoe(wi, ysp_i, ri, base - t)]
    out.append(star(cx, cy, n, 40, 24) + " " + circle(cx, cy, 7))
    top, h, w = 192, 72, 69
    for x in (cx - 3 - w, cx + 3):
        mx, my, d = x + w / 2, top + h / 2, 20
        out.append(rect(x, top, w, h) + " " + poly([(mx, my - d), (mx + d, my), (mx, my + d), (mx - d, my)]))
    return out


MOTIFS = {"zellij": zellij, "rosette": rosette, "warda": warda, "arch": arch}


def generate(spec):
    return MOTIFS[spec["motif"]](spec)


def build_svg(paths, title="design"):
    body = "\n".join(f'    <path d="{d}"/>' for d in paths)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{S:g}mm" height="{S:g}mm" viewBox="0 0 {S:g} {S:g}">
  <title>{escape(title)}</title>
  <rect id="background" width="{S:g}" height="{S:g}" fill="#ffffff"/>
  <g id="CUT" fill="#000000" fill-rule="evenodd" stroke="none">
{body}
  </g>
</svg>
'''
