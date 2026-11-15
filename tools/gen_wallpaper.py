#!/usr/bin/env python3
"""Generate a HyperOS-style abstract gradient wallpaper (pure stdlib PNG)."""
import zlib, struct, math, os

W, H = 1080, 2400

# HyperOS-ish colour stops (top -> bottom): deep navy -> blue -> purple -> violet
STOPS = [
    (0.00, (0x0B, 0x1C, 0x3D)),
    (0.30, (0x1E, 0x3A, 0x8A)),
    (0.62, (0x5B, 0x21, 0xB6)),
    (1.00, (0x9D, 0x4E, 0xDD)),
]

def stop_color(t):
    for i in range(len(STOPS) - 1):
        t0, c0 = STOPS[i]
        t1, c1 = STOPS[i + 1]
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
    return STOPS[-1][1]

# subtle horizontal + vertical brightness waves (cheap, precomputed)
hwave = [0.06 * math.sin(x / 160.0) for x in range(W)]
vwave = [0.06 * math.sin(y / 340.0) for y in range(H)]

def chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c

rows = bytearray()
for y in range(H):
    base = stop_color(y / (H - 1))
    g = 1.0 + vwave[y]
    # per-row: fill with base colour modulated by the horizontal wave (sampled)
    row = bytearray()
    for x in range(W):
        f = g + hwave[x]
        row += bytes((min(255, int(base[0] * f)),
                      min(255, int(base[1] * f)),
                      min(255, int(base[2] * f))))
    rows += b"\x00" + row  # PNG filter type 0 per scanline

ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)  # 8-bit, colour type 2 (RGB)
png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", ihdr)
       + chunk(b"IDAT", zlib.compress(bytes(rows), 6))
       + chunk(b"IEND", b""))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "downloads",
                   "hyperos_wallpaper.png")
out = os.path.abspath(out)
with open(out, "wb") as f:
    f.write(png)
print("wrote", out, len(png), "bytes")
