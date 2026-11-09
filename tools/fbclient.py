#!/usr/bin/env python3
"""Fastboot client over libusb for the Cubot KingKong Mini 3 (MTK Helix G85).

Platform-tools' libusb backend never enumerates this bootloader on Windows, so
we drive it directly. Framing is standard fastboot EXCEPT that packets carry no
4-hex length field: a packet is just 4 status bytes + raw payload.

    status := OKAY | FAIL | DATA | INFO
    INFO packets may repeat before the terminal status.

The multi-packet INFO stream was the source of two earlier misreads; a single
read() per command silently truncates the stream and desynchronises everything
after it.
"""
import sys
import usb.core
import usb.util
import usb.backend.libusb1
import libusb_package

VID, PID = 0x0E8D, 0x201C
CMD_TIMEOUT = 30000
PACKET_TIMEOUT = 4000


def backend():
    return usb.backend.libusb1.get_backend(find_library=libusb_package.find_library)


class Fastboot:
    def __init__(self):
        dev = usb.core.find(idVendor=VID, idProduct=PID, backend=backend())
        if dev is None:
            raise SystemExit("device not found %04x:%04x" % (VID, PID))
        self.dev = dev
        try:
            dev.set_configuration()
        except usb.core.USBError:
            pass
        cfg = dev.get_active_configuration()
        self.intf = cfg[(0, 0)]
        self.ep_out = usb.util.find_descriptor(
            self.intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        self.ep_in = usb.util.find_descriptor(
            self.intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
        usb.util.claim_interface(dev, self.intf.bInterfaceNumber)
        self.sync()

    def sync(self, tries=40):
        """Flush any queued/incomplete responses from an earlier session."""
        for _ in range(tries):
            try:
                self.ep_in.read(512, 120)
            except usb.core.USBError:
                return True
        try:
            self.dev.reset()
            usb.util.claim_interface(self.dev, self.intf.bInterfaceNumber)
        except Exception:
            pass
        return False

    def _packet(self, timeout=PACKET_TIMEOUT):
        d = bytes(self.ep_in.read(512, timeout))
        return d[:4].decode("ascii", "replace"), d[4:]

    def command(self, cmd, timeout=CMD_TIMEOUT):
        """Send a command; consume INFO packets until a terminal status."""
        self.ep_out.write(cmd.encode("ascii"), CMD_TIMEOUT)
        infos = []
        while True:
            status, payload = self._packet(timeout)
            if status == "INFO":
                infos.append(payload.decode("utf-8", "replace").rstrip("\x00"))
                continue
            return status, payload, infos

    def getvar(self, name):
        return self.command("getvar:" + name)

    def download(self, data):
        self.ep_out.write(("download:%08x" % len(data)).encode(), CMD_TIMEOUT)
        infos = []
        while True:
            status, payload = self._packet()
            if status == "INFO":
                infos.append(payload)
                continue
            break
        if status != "DATA":
            raise SystemExit("download refused: %s %r" % (status, payload))
        chunk = int(payload.decode("ascii", "replace").strip("\x00"), 16)
        sent = 0
        while sent < len(data):
            block = data[sent:sent + chunk]
            self.ep_out.write(block, CMD_TIMEOUT)
            st, _ = self._packet(20000)
            if st != "OKAY":
                raise SystemExit("chunk rejected at %d: %s" % (sent, st))
            sent += len(block)
        return chunk

    def close(self):
        try:
            usb.util.release_interface(self.dev, self.intf.bInterfaceNumber)
        except Exception:
            pass


def main():
    fb = Fastboot()
    args = sys.argv[1:]
    if not args:
        for v in ("product", "serialno", "unlocked", "secure", "max-download-size"):
            st, p, infos = fb.getvar(v)
            print("%-18s %-5s %s" % (v, st, p.decode("utf-8", "replace").strip("\x00")))
        fb.close()
        return
    st, p, infos = fb.command(" ".join(args), timeout=180000 if " " in " ".join(args) else CMD_TIMEOUT)
    for i in infos:
        print("INFO", i)
    print(st, p.decode("utf-8", "replace").strip("\x00"))
    fb.close()


if __name__ == "__main__":
    main()
