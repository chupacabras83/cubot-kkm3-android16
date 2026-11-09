import usb.core, usb.util, usb.backend.libusb1, libusb_package

be = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
dev = usb.core.find(idVendor=0x0E8D, idProduct=0x201C, backend=be)
try:
    dev.set_configuration()
except Exception:
    pass
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]
ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
usb.util.claim_interface(dev, 0)
try:
    while True:
        ep_in.read(512, 100)
except Exception:
    pass

# Non-destructive probes only. No reboot / powerdown / erase-of-real-partition.
probes = [
    "getvar:all",
    "getvar:version-bootloader",
    "getvar:partition-type:system",
    "download:00000000",
    "flash:doesnotexist",
    "erase:doesnotexist",
    "unlock",
    "oem-unlock",
    "oem_unlock",
    "getvar:unlocked",
]
for cmd in probes:
    ep_out.write(cmd.encode(), 30000)
    try:
        d = bytes(ep_in.read(512, 4000))
        print("%-32s -> %s" % (cmd, d[:80]))
        if cmd == "download:00000000" and d.startswith(b"DATA"):
            pass
    except Exception as e:
        print("%-32s -> TIMEOUT" % cmd)
