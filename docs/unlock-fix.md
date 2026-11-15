# Bootloader unlock — the correction

> **Status:** the earlier conclusion "this bootloader cannot be unlocked / there is no
> software path" was **wrong**. It was caused by a fastboot command-format bug, not by a
> locked-down bootloader. This page documents what actually happened and the correct
> procedure, so nobody repeats the mistake.

---

## 1. The wrong conclusion (and why it happened)

The previous round of on-device testing reported:

```
flashing:unlock     -> FAIL unknown command
oem unlock          -> FAIL unknown command
oem help            -> FAIL unknown command
```

and concluded the bootloader implements "no unlock command at all."

That was a **false negative**. The fastboot wire protocol uses a **space**, not a colon,
for the `flashing` and `oem` namespaces:

| Client command | Correct wire string | What the old notes sent |
|---|---|---|
| `fastboot flashing unlock` | `flashing unlock` | `flashing:unlock` ❌ |
| `fastboot flashing get_unlock_ability` | `flashing get_unlock_ability` | (never tested correctly) |
| `fastboot oem unlock` | `oem unlock` | `oem unlock` (this one *was* correct — the `oem` namespace is genuinely absent) |

Because the `flashing` probe used the colon form, the bootloader correctly answered
`unknown command`, and the investigation stopped there.

## 2. What the bootloader actually supports (re-tested on the device)

Using a from-scratch fastboot client (`tools/fbclient.py`) — needed because
platform-tools' libusb matcher rejects this bootloader's descriptor layout — the
correctly-formatted probes return:

```
getvar:product                  -> OKAY te155_cq_c031c_69_s0_eea
getvar:serialno                 -> OKAY KKMN3221011000106
getvar:unlocked                 -> OKAY no
getvar:secure                   -> OKAY yes
flashing get_unlock_ability     -> OKAY unlock_ability = 16777216   (0x01000000)
flashing get_unlocked           -> FAIL unknown command             (this verb is absent)
oem help                        -> FAIL unknown command             (no oem namespace)
```

Key facts:

- **The `flashing` namespace exists.** `flashing get_unlock_ability` answers OKAY.
- **`unlock_ability = 16777216`** (0x01000000) is the MediaTek "OEM unlock is allowed"
  flag being set — i.e. the *OEM unlocking* developer toggle is honoured. (When the
  toggle is off this returns 0.)
- `getvar:unlocked = no` → `secure = yes` is the **locked-but-unlockable** state.

## 3. The correct unlock procedure

1. On the phone: **Developer options → OEM unlocking → ON**, USB debugging ON.
   (`sys.oem_unlock_allowed` must read `1`.)
2. `adb reboot bootloader`
3. Drive the bootloader with `tools/fbclient.py` (platform-tools cannot enumerate it):

   ```
   python tools/fbclient.py "flashing unlock"
   ```

   `flashing unlock` (space, not colon) is recognised. The bootloader does **not** return
   OKAY immediately — it shows an on-screen confirmation and blocks.

4. **Physical step — cannot be automated.** The device displays the MediaTek
   "Unlock bootloader?" prompt and waits for a hardware keypress:
   - **Volume Up** = confirm (wipes all user data, sets the unlock flag, reboots)
   - **Volume Down** = cancel

   This is an intentional anti-theft measure. There is **no** USB/fastboot command,
   script, or PC privilege that can press this button. An actual person must press it
   on the device. This is the one step in the whole bring-up that can never be automated.

5. After the press, the phone wipes and reboots. Verify with:

   ```
   python tools/fbclient.py getvar:unlocked   # expect OKAY yes
   ```

## 4. Why platform-tools can't see this bootloader

The KKM3's LK advertises the fastboot class at **device level** rather than per-interface,
so platform-tools' libusb matcher never enumerates it (`fastboot devices` stays empty).
The custom client in `tools/fbclient.py` talks USB directly (VID `0x0E8D`, PID `0x201C`)
and speaks standard fastboot framing minus the 4-hex length field. See that file for the
exact framing details.
