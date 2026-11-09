# Credits

Everything working here is downstream of other people's labour. This project only
documents, verifies and automates; it does not build the ROMs.

## ROM builders

### Doze-off — Infinity X & Evolution X A16 GSIs
- https://github.com/Doze-off/ProjectInfinity-X_gsi — `Infinity X 3.12 | A16 QPR2 | TREBLE GSI`
- https://github.com/Doze-off/EvoX_treble — `Evolution X 11.11 | A16 QPR2 | TREBLE GSI`
- Also maintained by the same author: Lunaris-AOSP, Alphadroid, crDroid, PixelOS, ProjectSakura,
  Matrixx, Voltage, Rising-revived Treble GSIs.
- Support group: https://t.me/dozeoff_treble

Evolution X is the primary target here **because the Evolution X GSI incorporates AOSP
face unlock**, which the TrebleDroid base (and most other GSIs) does not ship.

### MisterZtr — LineageOS 23.x GSI
- https://github.com/MisterZtr/LineageOS_gsi
- Provides explicit **EXT4** and **EROFS** variants — critical for kernel-4.19 devices
  like this one, which cannot use EROFS. VNDK-version guidance in the release notes was
  used to confirm vendor/GSI compatibility.
- Built on the **RestlessOS** patch set (`cawilliamson/treble_restlessos`).

## Prior device work (the actual pioneers)

### klud (4pda)
First to boot **Android 13 and Android 14** GSIs on this exact model, and produced the
SuperiorOS A14 / crDroid 13 / crDroid 14 builds used by KKM3 owners. The SP Flash Tool
"Download Only" method this guide describes originates from klud's work, relayed by
badcodelab. Without it there would be no starting point.

### badcodelab (XDA)
Authored the *How to flash Android 13 and 14 GSI to KKM3 phone* write-up that made the
process reproducible, including the critical warning that `fastboot flash system` /
fastbootd is the wrong path on this device.
- https://xdaforums.com/t/installing-custom-rom-on-cubot-kingkong-mini.4050815/page-38

### Other KKM/KKM3 owners whose reports shaped this
- **cnfuzd** — first documented LeOS (A13) GSI running on a KKM3; Wi-Fi fix, face unlock failure
- **ylavi** — lock screen / FBE findings on KKM3; the crDroid 14 Bluetooth Mediatek workaround
- **Liquidator_** — confirmed SuperiorOS A14 installs and runs well; also flagged that
  Cubot's bundled SP Flash Tool has downloads disabled
- **birdibird** — KKM2 A16 QPR2 report (Infinity X, axion, LineageOS 23.2, crDroid 12.11, Baikal)
- **veloc_h**, **FasterPhoneMaster**, **pas-calc**, **jv81**, **BoubouLover**, **wifus**, **x53**
- **smartomato** (Hovatek) — first systematic KKM3 GSI/vbmeta experiments and OEM unlock confirmation

## Infrastructure

- **phhusson / TrebleDroid** — https://github.com/TrebleDroid/treble_experimentations
  The entire GSI ecosystem, the Treble app, and the patches everything above is built on.
- **Google** — AOSP GSI programme and reference Android 16 GSI binaries.
- **Cubot** — the stock firmware (`C031C_V07_20221014`) used as the recovery baseline.

## License note

The ROM images are **not** redistributed by this repository. They are downloaded
directly from their publishers' release pages and verified by SHA-256. Each upstream
project carries its own licence; consult those repositories before redistributing
binaries.
