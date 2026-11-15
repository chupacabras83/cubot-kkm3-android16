#!/usr/bin/env python3
"""Attempt `flashing unlock` (correct wire format) and report the result."""
import sys, time
sys.path.insert(0, ".")
from fbclient import Fastboot

def getvar_quiet(fb, name):
    try:
        st, p, infos = fb.command("getvar:" + name, timeout=8000)
        return st, p.decode("utf-8", "replace").strip("\x00").rstrip()
    except Exception as e:
        return "EXC", str(e)

fb = Fastboot()
st0, unlocked0 = getvar_quiet(fb, "unlocked")
print("before unlock -> %s %s" % (st0, unlocked0), flush=True)

try:
    st, payload, infos = fb.command("flashing unlock", timeout=30000)
    print("flashing unlock -> %s %r (INFO=%r)" % (st, payload, infos), flush=True)
except Exception as e:
    print("flashing unlock -> EXC %s" % e, flush=True)

# Give the bootloader a moment to act / reboot / wait for on-screen confirm
time.sleep(4)

# Re-check state; device may have rebooted (USB gone) or be waiting for keypress
try:
    st1, unlocked1 = getvar_quiet(fb, "unlocked")
    print("after unlock   -> %s %s" % (st1, unlocked1), flush=True)
except Exception as e:
    print("after unlock   -> device gone (rebooting?): %s" % e, flush=True)
