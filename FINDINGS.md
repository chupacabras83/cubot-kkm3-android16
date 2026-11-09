# Findings — what actually blocks Android 16 on this unit

**Device:** Cubot KingKong Mini 3 (`KINGKONGMINI3_EEA`), Helio G85 / MT6769V-CZ,
fingerprint `...:12/SP1A.210812.016/1670324649` (V07-era, December 2022 build).

Every conclusion below was tested on the hardware, not inferred from forum posts.

---

## 1. The bootloader has no unlock command

```
getvar:product    -> OKAY te155_cq_c031c_69_s0_eea
getvar:serialno   -> OKAY KKMN3221011000106
getvar:unlocked   -> OKAY no
getvar:secure     -> OKAY yes
getvar:max-download-size -> OKAY 0x8000000

flashing:unlock   -> FAIL unknown command
oem unlock        -> FAIL unknown command
oem help          -> FAIL unknown command
```

This firmware's LK implements `getvar:`, `download:`, `flash:` and little else. It does
not implement the `flashing:` namespace **or** the `oem` namespace, so
`fastboot flashing unlock` — the command every KKM3 guide depends on — cannot work here.

Why the community disagrees: those reports come from the **V08-era firmware**, where
Cubot evidently added unlock support. On the December 2022 build it is absent.

Consequence: no fastboot flashing of any kind. `system` lives inside `super`, so this is
fatal to the normal GSI install path.

## 2. Dynamic System Updates install correctly, then are ignored

DSU is the zero-risk route (guest image in `/data`, no partition writes). It was driven
directly, bypassing Settings:

```
am start-activity -n com.android.dynsystem/.VerificationActivity \
  -a android.os.image.action.START_INSTALL \
  --el android.os.image.key.SYSTEM_SIZE 3387408384 \
  --es android.os.image.key.URI file:///sdcard/Download/system16.img
```

Result — a genuine success at the install layer:

```
DynamicSystemService: startInstallation -> /data/gsi/dsu
notification: "Dynamic system is ready. To start using it, restart your device."
```

Then, after reboot:

```
ro.build.version.release   = 12      (stock, still)
ro.gsid.image_running      = (empty)
gsi_tool status            = normal
```

The image was accepted, staged, and then **the bootloader never booted it**. It fell back
to the normal system silently. This unit's MTK bootloader does not implement the DSU boot
path (`androidboot.dsu_switch` / GSI slot selection).

Image used was Google's **official signed** A16 GSI (`gsi_gms_arm64-exp-CP11.251209.009.A1`),
so this is not an AVB-signing rejection — it is the absence of DSU support.

## 3. Preloader/BROM entry lands in HID/META mode

With Volume Up held while connecting, the device enumerates as:

```
0e8d:20ff  "KINGKONG MINI 3"
  INTERFACE 0: Human Interface Device  (class 03 / 00 / 00)
    ENDPOINT 0x81  Interrupt IN   4 bytes
    ENDPOINT 0x01  Interrupt OUT  4 bytes
```

Four-byte interrupt endpoints. The MTK preloader/BROM protocol needs **bulk** endpoints;
`mtkclient` matches `0x20FF` as a MediaTek preloader but can only report
`Handshake failed, retrying...` against this HID interface. Running as root (permissions
are not the issue — verified with `chmod 666 /dev/bus/usb/...`) does not change it.

True BROM (`0e8d:0003`) never appears on this unit via key combinations. Reaching it
generally requires **shorting test points on the PCB** — a hardware operation.

## 4. Consequence

On this firmware revision there is **no software-only path to Android 16**:

| Route | Status |
|---|---|
| Official Cubot update | does not exist (Android 12 is the last) |
| `fastboot flashing unlock` | command absent from the bootloader |
| DSU / GSI as guest | installs fine, bootloader ignores it |
| `mtkclient` preloader | HID-only endpoints, handshake impossible |
| BROM (0x0003) | unreachable without test points |

Remaining option is physical: disassemble, locate the test points, short them to force
BROM, then `mtkclient` can dump and write flash. That is a hardware project with real
risk and is out of scope for software automation.

## 5. What is not the problem

- Not AVB signing — Google's signed GSI was rejected the same way.
- Not USB drivers — adb and the fastboot protocol were both driven successfully
  (see `tools/fbclient.py`, a from-scratch fastboot client; platform-tools' libusb
  matcher rejects this bootloader's descriptor layout, which advertises the fastboot
  class at device level rather than per-interface).
- Not SELinux — `chmod 666` on the usb node as root removed every permission error.
- Not the GSI — both images verified ext4, correct ABI, correct VNDK target.
