import usb.core, usb.util, usb.backend.libusb1, libusb_package, time

be = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)
dev = usb.core.find(idVendor=0x0E8D, idProduct=0x201C, backend=be)
if dev is None:
    raise SystemExit("device gone")
print("found, resetting...")
try:
    dev.reset()
    print("reset OK")
except Exception as e:
    print("reset failed:", e)
time.sleep(2)

dev = usb.core.find(idVendor=0x0E8D, idProduct=0x201C, backend=be)
if dev is None:
    raise SystemExit("device vanished after reset")
try:
    dev.set_configuration()
except Exception:
    pass
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]
ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
usb.util.claim_interface(dev, 0)

# flush
try:
    while True:
        ep_in.read(512, 100)
except Exception:
    pass

for cmd in ["getvar:product", "getvar:unlocked"]:
    try:
        ep_out.write(cmd.encode(), 5000)
        d = bytes(ep_in.read(512, 3000))
        print("%-20s -> %s" % (cmd, d))
    except Exception as e:
        print("%-20s -> FAILED %s" % (cmd, e))
