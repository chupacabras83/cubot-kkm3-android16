#!/usr/bin/env python3
"""Download the Infinity X 3.12 A16 QPR2 GAPPS GSI and verify SHA-256.

Streams to disk, prints progress, writes .sha256 on success.
"""
import sys, hashlib, urllib.request, os, time

URL = "https://github.com/Doze-off/ProjectInfinity-X_gsi/releases/download/2026-09-20/Infinity-X-3.12-GSI_treble_arm64-ab-GAPPS-Official-20260920.img.xz"
SHA = "18e9d0807b42cdd0f35e52f4f0dd5782e65f7dd52ae150e61b54fa1106ffa233"
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "downloads",
                    "Infinity-X-3.12-arm64-ab-GAPPS.img.xz")
DEST = os.path.abspath(DEST)
PART = DEST + ".part"

def main():
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    start = os.path.getsize(PART) if os.path.exists(PART) else 0
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/octet-stream",
    })
    if start:
        req.add_header("Range", "bytes=%d-" % start)
    print("dest=%s start=%d" % (DEST, start), flush=True)
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=60) as r:
        total = int(r.headers.get("Content-Length") or 0) + start
        mode = "ab" if start else "wb"
        done = start
        t0 = time.time()
        with open(PART, mode) as f:
            while True:
                block = r.read(1024 * 1024)
                if not block:
                    break
                f.write(block)
                h.update(block)
                done += len(block)
                if total:
                    pct = done * 100.0 / total
                    mb = done / 1e6
                    rate = done / (time.time() - t0 + 1e-9) / 1e6
                    print("\r%6.2f%%  %8.1f MB  %5.1f MB/s" % (pct, mb, rate),
                          end="", flush=True)
    print("\nfinished. verifying sha256...", flush=True)
    got = h.hexdigest()
    ok = got == SHA
    if ok:
        os.replace(PART, DEST)
        with open(DEST + ".sha256", "w") as fh:
            fh.write(got + "  " + os.path.basename(DEST) + "\n")
        print("OK sha256 matches:", got, flush=True)
    else:
        print("MISMATCH\ngot:  %s\nwant: %s" % (got, SHA), flush=True)
        sys.exit(2)

if __name__ == "__main__":
    main()
