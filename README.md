# Cubot KingKong Mini 3 — Android 16 (GSI) Bring-Up

Bringing **Android 16 (API 36, QPR2)** to the Cubot KingKong Mini 3, a 2022 MediaTek
Helio G85 handset that Cubot abandoned on **Android 12**. There is no official update and
no device-specific custom ROM; this project documents and automates the **Treble GSI**
route, and tracks what does and does not work.

> **Status: IN PROGRESS.** Images staged and verified. Flashing blocked on two local
> hardware gates (bootloader driver + physical unlock confirmation) — see [Blockers](#blockers).

---

## Device

| | |
|---|---|
| Model | Cubot KingKong Mini 3 (`KINGKONGMINI3_EEA`) |
| SoC | MediaTek **Helio G85 / MT6769V-CZ** (8 core) |
| Kernel | **4.19.191** (non-GKI) |
| Shipped OS | **Android 12 / API 31**, security patch 2022-12-05 |
| RAM / Storage | 6 GB / 128 GB |
| Display | 480 × 1170 @ 204 dpi |
| ABI | arm64-v8a |
| Partitions | **A-only**, dynamic (`super` → ext4 `system`/`vendor`/`product`) |
| Treble | `ro.treble.enabled=true`, **VNDK 31**, not lite |
| AVB | 1.2, `verifiedbootstate=green`, verity enforcing |

### Two facts that decide everything

1. **Kernel 4.19 ⇒ EXT4 system images only.** EROFS requires kernel 5.4+. Any EROFS GSI
   will not boot here. Both staged images are verified ext4 (superblock magic `0x53EF`).
2. **Vendor is stock and stays stock.** A GSI replaces the `system` partition only. The
   `vendor` partition — every driver — is untouched. This is why "porting" an A14 ROM
   forward is not a thing: there is nothing to port, only a system image to swap.

---

## Images (verified)

| Image | Android | FS | Size | SHA-256 |
|---|---|---|---|---|
| Infinity X 3.12 `arm64-ab` VANILLA | 16 QPR2 | ext4 | 2.74 GB | `422c93a3…b1ea39` |
| Evolution X 11.11 `arm64-ab` VANILLA | 16 QPR2 | ext4 | 3.17 GB | `f3f8bc5a…8353705` |

Both SHA-256 values were checked against the publisher's release digest and matched.
Evolution X is the primary target — it ships AOSP face unlock, and this device has a
genuine face HAL (below).

---

## Face unlock: why this might actually work

Most Cubot GSI reports say "no face unlock". That is a **GSI limitation, not a hardware
one** — and this device is better than most:

```
/vendor/lib64/android.hardware.biometrics.face@1.0.so
/vendor/lib64/libstfaceunlock.so
/vendor/lib64/libcv_faceid.so
feature:android.hardware.biometrics.face
```

Cubot shipped a **real HIDL face HAL** (STMicroelectronics stack `libstfaceunlock` /
`libcv_faceid`) and the biometrics feature flag, not a framework-only hack. A GSI that
implements the AOSP face-unlock UI and client — Evolution X, or ponces' AOSP — can
therefore talk to it. Untested on this model; this project exists to test it.

Camera: `android.hardware.camera.provider` is present, so GSI camera support is
available through the vendor provider HAL.

---

## Blockers

| # | Blocker | Why it cannot be automated |
|---|---|---|
| 1 | Bootloader USB driver | WinUSB binding for `0E8D:201C` needs `pnputil` + admin → UAC prompt |
| 2 | `fastboot flashing unlock` | Requires **Volume Up** on the device |
| 3 | Data wipe | Unavoidable on unlock; `/sdcard` must be pulled first |
| 4 | Stock recovery image | cubot.net is TLS-unreachable from the build host; Drive mirror is quota-blocked |

Mitigation for #4: flash **`system` only** over fastboot. This leaves `boot`, `vendor`,
`vbmeta` and the `super` metadata intact, so a failed GSI can be replaced with another
GSI without needing the stock ROM. This is the lower-risk path and is what this project
uses by default.

---

## Credits

This project stands entirely on other people's work. See [CREDITS.md](CREDITS.md).

- **Doze-off** — Infinity X and Evolution X A16 Treble GSIs
- **MisterZtr** — LineageOS 23.x GSI (ext4/EROFS variants)
- **klud** (4pda) — the Android 13/14 GSI bring-up for this exact device
- **badcodelab**, **cnfuzd**, **ylavi**, **Liquidator_**, **birdibird** (XDA) — device reports
- **phhusson / TrebleDroid** — the GSI infrastructure everything here depends on

No warranty. Flashing is at your own risk.
