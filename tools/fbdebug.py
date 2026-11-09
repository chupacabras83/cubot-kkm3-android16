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
print("ep_in", hex(ep_in.bEndpointAddress), "ep_out", hex(ep_out.bEndpointAddress), "maxpacket", ep_in.wMaxPacketSize)

for cmd in ["getvar:version", "getvar:product"]:
    print("\n>>>", cmd)
    ep_out.write(cmd.encode(), 20000)
    try:
        d = bytes(ep_in.read(64, 20000))
        print("raw:", d.hex(), "| ascii:", d)
    except Exception as e:
        print("read err:", e)
        try:
            d = bytes(ep_in.read(4, 20000))
            print("4-byte:", d.hex(), d)
        except Exception as e2:
            print("second read err:", e2)
