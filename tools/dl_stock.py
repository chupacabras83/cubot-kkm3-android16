#!/usr/bin/env python3
"""Download the official Cubot KKM3 V07 stock firmware (restore lifeline) from mega.nz."""
import os, sys, time
from mega import Mega

ROM_URL = "https://mega.nz/file/4QMwDZza#H66JQr7f1F0kL0mKl5WjBLNZTJ5L4r2qQIkqdecnNZA"
DEST_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "downloads"))
DEST_NAME = "stock_C031C_V07_20221014.zip"

def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    dest = os.path.join(DEST_DIR, DEST_NAME)
    if os.path.exists(dest) and os.path.getsize(dest) > 100_000_000:
        print("already present:", dest, os.path.getsize(dest), flush=True)
        return
    mega = Mega()
    m = mega.login()
    print("anonymous login OK, starting ROM download...", flush=True)
    t0 = time.time()
    path = m.download_url(ROM_URL, dest_path=DEST_DIR, dest_filename=DEST_NAME)
    print("done in %.0fs -> %s" % (time.time() - t0, path), flush=True)
    print("size:", os.path.getsize(path), flush=True)

if __name__ == "__main__":
    main()
