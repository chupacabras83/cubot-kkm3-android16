# Android 16 flash & boot — what actually worked

> Result: **Android 16 (API 36) is running on the Cubot KingKong Mini 3.**
> This is the exact procedure that worked, on-device, on 2026-11-16.

---

## 1. Outcome

| Item | Result |
|---|---|
| OS | **Android 16** (`ro.build.version.release=16`, SDK 36) |
| Build | Infinity X 3.12 GSI (`infinity_gsi-user`, `BP4A.251205.006 release-keys`) |
| Security patch | **2026-09-01** |
| Boot | `sys.boot_completed = 1` |
| IMEI | `863088060001063` — **preserved** (vendor untouched) |
| Modem/baseband | `E155_69_S0_LWTG_V0.0.8` — intact |
| Wi-Fi | enabled / working |
| Bluetooth | enabled |
| Camera | 2 devices detected (vendor HAL) |

## 2. Assets staged

- **GSI**: `Infinity-X-3.12-GSI_treble_arm64-ab-GAPPS-Official-20260920.img.xz`
  - SHA-256 `18e9d0807b42cdd0f35e52f4f0dd5782e65f7dd52ae150e61b54fa1106ffa233`
  - Decompressed 3,458,613,248 bytes, **ext4** (`magic 0x53EF @ 0x438`) — EROFS would not
    boot on this 4.19 kernel.
- **Stock firmware** (brick-recovery lifeline): `C031C_V07_20221014` (scatter + `super.img`,
  `boot.img`, `recovery.img`, `vbmeta*.img`, `md1img.img`, and the `DATABASE/` APDB+MDDB
  files needed for IMEI repair via SN Writer).

## 3. Flash procedure (fastbootd route — this is what worked)

The raw bootloader (`0E8D:201C`) does **not** expose logical partitions, but the device's
**fastbootd** (userspace fastboot) does — and unlike the bootloader, platform-tools
enumerates fastbootd normally. This is the key that unblocked the flash.

```powershell
# prerequisites: bootloader UNLOCKED (see unlock-fix.md), GSI decompressed to .img
adb reboot fastboot              # enter fastbootd
fastboot getvar is-userspace     # -> yes
fastboot getvar is-logical:system  # -> yes

fastboot delete-logical-partition product   # frees ~2 GiB in super
fastboot flash system Infinity-X-3.12-arm64-ab-GAPPS.img   # resizes system, 13 sparse chunks
fastboot reboot
```

Partition math (why `product` had to go):

| Partition | Size |
|---|---|
| system | 1.37 GiB |
| vendor | 611 MiB |
| product | 1.97 GiB |
| super (total) | 4.5 GiB |

GSI is 3.22 GiB, so `product` (1.97 GiB) is deleted and `system` grows to fit.

### vbmeta note

`fastboot flash vbmeta` is **refused by fastbootd** (`Writing 'vbmeta' FAILED remote:
'No such file or directory'` — fastbootd can't reach that physical partition on this
device). It did not matter: with the bootloader **unlocked (`orange` state)**, AVB is not
enforced and the unsigned GSI boots. A pre-patched `vbmeta_disabled.img` (flags `0x3`) was
prepared as a fallback but was not needed.

## 4. First-boot fix (required — otherwise a crash loop)

Symptom: `android.process.media` crashing repeatedly:

```
SQLiteException: Can't downgrade database from version 116 to 114
... Unable to get provider com.android.providers.downloads.DownloadProvider
```

Cause: the stock Android 12 `/data` media/download databases were at a higher schema
version than the GSI expects. Fix (clears the stale DBs so they rebuild):

```powershell
adb shell pm clear com.android.providers.downloads
adb shell pm clear com.android.providers.downloads.ui
adb shell pm clear com.android.providers.media.module
adb shell pm clear com.android.externalstorage
adb shell pm clear com.android.providers.media
```

After this, `android.process.media` is stable and no new FATAL exceptions appear.

## 5. Post-boot Treble fixes (expect these on this device)

- **VoLTE / IMS** — Phh/Treble Settings → IMS features → *Request IMS network* +
  *Force presence of 4G*; install the MediaTek IMS app.
- **Bluetooth** — Treble Settings → Misc → Bluetooth workarounds → **Mediatek**.
- **BT audio silent** — Misc → disable audio effects / alternate headset route.
- **Wi-Fi / firewall** — Misc → *Universal legacy-kernel BPF fallback*.
- **Jittery UI** — `adb shell cmd package compile -m everything -a`.

## 6. What is preserved vs lost

Preserved (vendor partition is never touched by a GSI): camera HAL, modem/radio, IMEI/NVRAM,
Wi-Fi/Bluetooth drivers, fingerprint/face HAL, all sensors.

Lost/expected: Widevine L1→L3, face unlock (unverified), no OTA, Play Integrity may fail.
The `product` partition was deleted to make room (a GSI does not need it).
