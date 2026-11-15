#!/usr/bin/env python3
"""Decompress the GSI .img.xz -> .img (streaming) and verify ext4 magic."""
import lzma, os, sys, time

SRC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "..", "downloads", "Infinity-X-3.12-arm64-ab-GAPPS.img.xz"))
DST = SRC[:-3]  # strip .xz

def main():
    print("src:", SRC, flush=True)
    print("dst:", DST, flush=True)
    if os.path.exists(DST):
        print("already decompressed:", DST, flush=True)
    else:
        t0 = time.time()
        n = 0
        with lzma.open(SRC, "rb") as f, open(DST + ".part", "wb") as o:
            while True:
                b = f.read(8 * 1024 * 1024)
                if not b:
                    break
                o.write(b)
                n += len(b)
                if n % (256 * 1024 * 1024) < (8 * 1024 * 1024):
                    print("\r%8.1f MB  %5.1f MB/s" % (n / 1e6, n / (time.time() - t0 + 1e-9) / 1e6),
                          end="", flush=True)
        os.replace(DST + ".part", DST)
        print("\ndecompressed %d bytes in %.0fs" % (n, time.time() - t0), flush=True)

    # verify ext4 magic 0xEF53 at offset 0x438 (little-endian -> b'\x53\xef')
    with open(DST, "rb") as f:
        f.seek(0x438)
        magic = f.read(2)
    ok = magic == b"\x53\xef"
    print("ext4 magic @0x438: %s -> %s" % (magic.hex(), "EXT4 OK" if ok else "NOT EXT4 (EROFS?)"), flush=True)
    sys.exit(0 if ok else 3)

if __name__ == "__main__":
    main()
