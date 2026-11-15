#!/usr/bin/env python3
"""Enumerate the MediaTek USB device currently attached and report mode/endpoints.

Used to tell apart preloader (VCOM bulk, flashable) vs META/HID (interrupt-only)
vs fastboot vs adb.
"""
import usb.core, usb.util, usb.backend.libusb1, libusb_package, time

be = usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)

def dump(pid):
    dev = usb.core.find(idVendor=0x0E8D, idProduct=pid, backend=be)
    if dev is None:
        print("no device 0e8d:%04x" % pid)
        return
    print("=== 0e8d:%04x ===" % pid)
    try:
        print("manufacturer:", dev.manufacturer)
        print("product     :", dev.product)
    except Exception as e:
        print("strings unavail:", e)
    for cfg in dev:
        print("  config bConfigurationValue=%d" % cfg.bConfigurationValue)
        for intf in cfg:
            print("    interface %d  class=%d subclass=%d proto=%d" %
                  (intf.bInterfaceNumber, intf.bInterfaceClass,
                   intf.bInterfaceSubClass, intf.bInterfaceProtocol))
            for ep in intf:
                d = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
                t = {usb.util.ENDPOINT_TYPE_BULK: "BULK",
                     usb.util.ENDPOINT_TYPE_INTR: "INTERRUPT",
                     usb.util.ENDPOINT_TYPE_ISO: "ISO"}.get(usb.util.endpoint_type(ep.bmAttributes), "?")
                print("      ep 0x%02x  %s  %s" % (ep.bEndpointAddress, d, t))

# poll the current mode for a few seconds to see if it is stable or transient
for i in range(3):
    dev = usb.core.find(idVendor=0x0E8D, backend=be)
    pid = None
    if dev is not None:
        pid = dev.idProduct
    print("sample %d: idProduct=%s" % (i, "0x%04x" % pid if pid else "None"))
    if pid is not None:
        dump(pid)
        break
    time.sleep(2)
