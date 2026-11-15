#!/usr/bin/env python3
"""Non-destructive probe of the KKM3 bootloader's fastboot command vocabulary.

Reads ONLY. Sends no erase/flash/unlock/reboot commands. Uses the fbclient
transport because platform-tools cannot enumerate this bootloader's descriptor.
"""
import sys, time
sys.path.insert(0, ".")
from fbclient import Fastboot

# Safe, read-only commands. Deliberately NOT including the destructive unlock verbs.
PROBES = [
    "getvar:product",
    "getvar:serialno",
    "getvar:unlocked",
    "getvar:secure",
    "getvar:unlock_ability",
    "getvar:version-bootloader",
    "getvar:version-baseband",
    "getvar:max-download-size",
    "getvar:partition-type:system",
    "getvar:partition-type:boot",
    "getvar:all",
    "oem help",
    "flashing get_unlock_ability",
    "flashing get_unlocked",
    "oem get_unlock_status",
    "oem get_unlock_ability",
]

def main():
    fb = Fastboot()
    print("== connected to bootloader ==")
    for cmd in PROBES:
        try:
            st, payload, infos = fb.command(cmd, timeout=12000)
        except Exception as e:
            print("[%-32s] EXC %s" % (cmd, e))
            continue
        line = payload.decode("utf-8", "replace").strip("\x00").rstrip()
        if infos:
            for i in infos:
                print("[%-32s] INFO %s" % (cmd, i.rstrip("\x00")))
        print("[%-32s] %-4s %s" % (cmd, st, line))
    fb.close()

if __name__ == "__main__":
    main()
