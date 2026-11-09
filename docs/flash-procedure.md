# Flash Procedure — KK Mini 3 → Android 16 GSI

Two paths exist. **Path A (recommended)** touches only the `system` partition and keeps
`boot`/`vendor`/`vbmeta` intact, so a bad image is recoverable by flashing another GSI.
**Path B** is the historical SP Flash Tool method used by klud and the only one documented
end-to-end on this model — but it writes raw images and can wipe the TEE/IMEI if
misfired. Prefer A.

---

## 0. Prerequisites

- Bootloader **unlocked** (`fastboot flashing unlock`, confirmed with Volume Up)
- Windows with **WinUSB bound to `0E8D:201C`** (the fastboot interface)
  ```
  pnputil /add-driver %WINDIR%\INF\winusb.inf /install
  pnputil /scan-devices
  fastboot devices      # must list KKMN3221011000106
  ```
  Requires an elevated prompt. Without it fastboot reports `< waiting for any device >`
  and the phone appears in Device Manager as an unbound `Android` device.
- A GSI **ext4** image (never EROFS — kernel 4.19)

## 1. Back up before anything else

Unlocking the bootloader and flashing both erase userdata.

```powershell
adb pull /sdcard E:\kk3-backup\sdcard
adb shell pm list packages -f > E:\kk3-backup\packages.txt
adb shell dumpsys battery > E:\kk3-backup\battery.txt
```

Record the IMEI(s) from `*#06#` or the retail box. This is the single most important
step — a botched SP Flash Tool run can wipe NVRAM and leave
`TEE key not write / Google key not write` with no mobile network.

## 2. Unlock

```powershell
adb reboot bootloader
fastboot flashing unlock      # confirm with VOLUME UP on the phone
fastboot reboot bootloader
```

`fastboot flashing get_unlock_ability` should return `1` beforehand.

## 3. Verify the image, then flash (Path A)

```powershell
# confirm ext4 magic 0x53EF at offset 0x438 before trusting the file
python -c "f=open('EvoX-11.11-arm64-ab-VANILLA.img','rb'); f.seek(1080); print(f.read(2).hex())"
# expect: ef53

adb reboot bootloader
fastboot reboot fastboot          # enter fastbootd
fastboot delete-logical-partition product   # frees room in super for a ~3 GB system
fastboot flash system EvoX-11.11-arm64-ab-VANILLA.img
fastboot reboot
```

If you need to roll back inside Path A, simply flash the other GSI. Nothing outside
`system` was modified.

### If fastbootd refuses
That is the known failure mode on this device (2022 reports: stuck at the Cubot logo).
Fall through to Path B.

## 4. Path B — SP Flash Tool (klud's method)

1. Install **SP Flash Tool v5.2104 or v5.1924**. v6 cannot load scatter files. Cubot's
   bundled copy has downloads disabled — use the upstream one.
2. Load the stock scatter file from `C031C_V07_20221014`.
3. Deselect everything, then select **only** the GSI `system.img`.
4. Mode: **Download Only** — *never* "Format All + Download".
5. Power the phone off, press Download, then connect USB (BROM/preloader window is short).
6. First boot 5–15 min.

## 5. First-boot fixes (expect to need these)

```powershell
adb shell settings put global restricted_networking_mode 0
```

- **VoLTE / IMS** — Treble Settings → IMS features → enable *Request IMS network* and
  *Force the presence of 4G*; install the MediaTek IMS app; reboot.
- **Bluetooth** — Treble Settings → Misc → Bluetooth workarounds → **Mediatek**
  (confirmed necessary on this device with crDroid 14).
- **BT audio silent** — Misc → disable audio effects / alternate headset route.
- **Wi-Fi / firewall oddities** — Misc → *Universal legacy-kernel BPF fallback*.
- **Jittery UI** — let it settle ~1 h, or `adb shell cmd package compile -m everything -a`.

## 6. Known losses

- Widevine L1 → L3 (no HD streaming); only reversible by returning to stock + relocking.
- Face unlock: **test target**, see README. Expected to work via Evolution X's AOSP face
  unlock against the vendor face HAL; unproven on this model.
- Camera: functions through `camera.provider`, quality typically below stock.
- No OTA — every monthly security patch means re-flashing.
- Lock screen / FBE: mixed reports on this device. **Verify a lock screen works on day one**
  before trusting the phone with anything.
