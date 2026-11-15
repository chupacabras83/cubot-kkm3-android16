# Monitor: wait for the Cubot to leave fastboot (unlock) and return to ADB.
# Exits 0 and writes a marker when detected; exits 1 on timeout.
$adb = "C:\Users\iMac2019\AppData\Local\Android\Sdk\platform-tools\adb.exe"
$s = "KKMN3221011000106"
$marker = "kk3-android16\backup\unlock_detected.txt"
$deadline = (Get-Date).AddMinutes(30)
Write-Output "monitor started at $(Get-Date -Format o); waiting for $s in adb devices"
while ((Get-Date) -lt $deadline) {
    $d = & $adb devices 2>$null
    if ("$d" -match $s) {
        $msg = "unlock reboot detected at $(Get-Date -Format o)"
        Set-Content -Path $marker -Value $msg
        Write-Output "DETECTED -> $d"
        exit 0
    }
    Start-Sleep -Seconds 5
}
Write-Output "TIMEOUT after 30 min; device did not return to adb"
exit 1
