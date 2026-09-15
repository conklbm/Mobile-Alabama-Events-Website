"""Render favicon.ico + PNGs from the on-brand icon.svg. Run once; outputs are committed.

    uv run python scripts/make_favicons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

STATIC = Path(__file__).resolve().parent.parent / "pipeline" / "publish" / "static"


def draw(size: int) -> Image.Image:
    # Same mark as icon.svg: rounded blue tile, two waves, orange sun.
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = s * 14 // 64
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=(11, 92, 143, 255))
    w = max(2, s * 5 // 64)
    for y, color in ((40, (255, 255, 255, 255)), (50, (224, 122, 31, 255))):
        pts = []
        import math
        for x in range(8 * s // 64, 56 * s // 64 + 1):
            t = (x - 8 * s / 64) / (48 * s / 64) * 3 * math.pi
            pts.append((x, y * s / 64 + math.sin(t) * (4 * s / 64)))
        d.line(pts, fill=color, width=w, joint="curve")
    cx, cy, rr = 46 * s // 64, 18 * s // 64, 7 * s // 64
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(224, 122, 31, 255))
    return img


def main() -> None:
    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        draw(size).save(STATIC / name)
    draw(64).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("wrote favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png")


if __name__ == "__main__":
    main()
