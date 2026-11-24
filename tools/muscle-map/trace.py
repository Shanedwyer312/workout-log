"""Trace the color-coded muscle chart into SVG path data for SetRep.
Usage: python3 trace.py source.png out.js [preview.png]
"""
import sys, json
import numpy as np, cv2

SRC, OUT = sys.argv[1], sys.argv[2]
PREVIEW = sys.argv[3] if len(sys.argv) > 3 else None

PAL = {
    "chest": "#E6194B", "front_delts": "#F58231", "side_delts": "#FFE119", "rear_delts": "#9A6324",
    "traps": "#42D4F4", "biceps": "#4363D8", "triceps": "#911EB4", "forearms": "#F032E6",
    "abs": "#3CB44B", "obliques": "#BFEF45", "lats": "#000075", "upper_back": "#469990",
    "lower_back": "#800000", "glutes": "#FABED4", "quads": "#808000", "hamstrings": "#DCBEFF",
    "adductors": "#AAFFC3", "calves": "#FFD8B1",
    "_skin": "#A9A9A9", "_line": "#000000", "_bg": "#FFFFFF",
}
names = list(PAL)
cols = np.array([[int(PAL[n][i:i+2], 16) for i in (1, 3, 5)] for n in names], np.float32)

img = cv2.imread(SRC)[:, :, ::-1].astype(np.float32)  # RGB
img = cv2.medianBlur(img.astype(np.uint8), 3).astype(np.float32)
H, W, _ = img.shape
# nearest palette colour per pixel (in a perceptual-ish space)
lab = cv2.cvtColor((img).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
pal_lab = cv2.cvtColor(cols.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
d = ((lab[:, :, None, :] - pal_lab[None, None, :, :]) ** 2).sum(-1)
label = d.argmin(-1)

idx = {n: i for i, n in enumerate(names)}
body = (label != idx["_bg"]).astype(np.uint8)
body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

SCALE = 0.5  # output units = half pixels


def smooth_path(pts):
    """closed polyline -> smooth cubic bezier path (Catmull-Rom)"""
    n = len(pts)
    if n < 3:
        return ""
    P = [(p[0] * SCALE, p[1] * SCALE) for p in pts]
    out = [f"M{P[0][0]:.1f} {P[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(out) + "Z"


def mask_paths(mask, min_area=40, eps=1.2):
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    paths = []
    if hier is None:
        return paths
    hier = hier[0]
    for i, c in enumerate(cnts):
        if hier[i][3] != -1:
            continue  # holes are added to their parent below
        if cv2.contourArea(c) < min_area:
            continue
        d = smooth_path(cv2.approxPolyDP(c, eps, True)[:, 0, :].tolist())
        j = hier[i][2]
        while j != -1:
            if cv2.contourArea(cnts[j]) >= min_area:
                d += smooth_path(cv2.approxPolyDP(cnts[j], eps, True)[:, 0, :].tolist())
            j = hier[j][0]
        paths.append((cv2.contourArea(c), d))
    return paths


# split into the two views at the widest white gap in the middle
cols_body = body.sum(0)
mid = W // 2
gap = [x for x in range(int(W * 0.35), int(W * 0.65)) if cols_body[x] == 0]
split = int(np.median(gap)) if gap else mid

views = {}
for vname, (x0, x1) in {"front": (0, split), "back": (split, W)}.items():
    sub = np.zeros_like(body); sub[:, x0:x1] = body[:, x0:x1]
    ys, xs = np.nonzero(sub)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = 6
    vb = [round((bx0 - pad) * SCALE, 1), round((by0 - pad) * SCALE, 1),
          round((bx1 - bx0 + 2 * pad) * SCALE, 1), round((by1 - by0 + 2 * pad) * SCALE, 1)]
    sil = [p for _, p in sorted(mask_paths(sub, 200, 1.0), reverse=True)]
    region = np.zeros_like(body); region[:, x0:x1] = 1
    skin = (label == idx["_skin"]).astype(np.uint8) * region
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    skin_p = [p for _, p in mask_paths(skin, 60)]
    regions = []
    for m in names:
        if m.startswith("_"):
            continue
        mk = (label == idx[m]).astype(np.uint8) * region
        mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        for area, p in sorted(mask_paths(mk, 80), reverse=True):
            regions.append([m, p])
    ln = (label == idx["_line"]).astype(np.uint8) * region * body
    lines = "".join(p for _, p in mask_paths(ln, 6, 0.7))
    views[vname] = {"viewBox": " ".join(map(str, vb)), "sil": "".join(sil), "skin": skin_p, "regions": regions, "lines": lines}
    print(vname, "viewBox", vb, "regions", len(regions), "skin", len(skin_p),
          {m: sum(1 for r in regions if r[0] == m) for m in names if not m.startswith("_")})

with open(OUT, "w") as f:
    f.write("/* Muscle map shapes traced from a colour-coded anatomy chart (tools: trace.py).\n"
            "   Each view: viewBox, sil (whole body outline), skin (non-muscle areas), regions [muscle key, path]. */\n")
    f.write("const BODY_VIEWS=" + json.dumps(views, separators=(",", ":")) + ";\n")

if PREVIEW:
    vis = np.full((H, W, 3), 255, np.uint8)
    vis[body > 0] = (20, 20, 20)
    for n in names:
        if n in ("_bg", "_line"):
            continue
        vis[(label == idx[n]) & (body > 0)] = cols[idx[n]].astype(np.uint8)
    cv2.imwrite(PREVIEW, vis[:, :, ::-1])
