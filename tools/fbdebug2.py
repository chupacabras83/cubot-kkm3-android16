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

print("--- drain start ---")
try:
    while True:
        d = bytes(ep_in.read(512, 100))
        print("  stale:", d.hex(), d)
except Exception:
    print("  drained (no more data)")

seq = ["getvar:product", "getvar:serialno", "getvar:unlocked", "oem help", "flashing:unlock"]
for cmd in seq:
    print("\n>>>", repr(cmd))
    ep_out.write(cmd.encode(), 30000)
    try:
        d = bytes(ep_in.read(512, 5000))
        print("   raw hex:", d.hex())
        print("   ascii  :", d)
    except Exception as e:
        print("   TIMEOUT/err:", e)
