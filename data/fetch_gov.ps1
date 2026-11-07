# Windows version of data/fetch_gov.sh: downloads the Hakka Affairs Council 115年度 certification
# vocabulary tables (.ods, all five accents, all levels) into a folder "hakka-gov-115" and zips it.
# Run in PowerShell:   powershell -ExecutionPolicy Bypass -File fetch_gov.ps1
# Optional:            -Audio  (also Sixian + Hailu audio, large)
param([switch]$Audio)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$out = Join-Path (Get-Location) "hakka-gov-115"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$base = "https://elearning.hakka.gov.tw/hakka/files/downloads"

function Get-File($id, $ext, $name) {
  $f = Join-Path $out "$name.$ext"
  if ((Test-Path $f) -and ((Get-Item $f).Length -gt 0)) { Write-Host "have $name"; return }
  $part = "$f.part"   # download to .part, rename when complete: an interrupted file is fetched again next run
  try {
    Invoke-WebRequest -UseBasicParsing -Uri "$base/$id.$ext" -OutFile $part
    Move-Item -Force $part $f
    Write-Host "ok   $name.$ext"
  } catch { Write-Host "FAIL $base/$id.$ext" -ForegroundColor Red; Remove-Item -ErrorAction SilentlyContinue $part }
}

$accents = "sixian", "hailu", "dapu", "raoping", "zhaoan"
for ($i = 0; $i -lt 5; $i++) {
  $a = $accents[$i]
  Get-File (761 + 6*$i) "ods" "basic_vocab_$a"
  Get-File (762 + 6*$i) "ods" "elementary_vocab_$a"
  Get-File (763 + 6*$i) "ods" "basic_elementary_bank_$a"
  Get-File (736 + 5*$i) "ods" "intermediate_vocab_$a"
  Get-File (737 + 5*$i) "ods" "upper_intermediate_vocab_$a"
  Get-File (797 + 4*$i) "ods" "advanced_vocab_$a"
}
if ($Audio) {
  Get-File 766 "zip" "basic_elementary_audio_sixian"; Get-File 772 "zip" "basic_elementary_audio_hailu"
  Get-File 740 "zip" "intermediate_audio_sixian";     Get-File 745 "zip" "intermediate_audio_hailu"
  Get-File 800 "zip" "advanced_audio_sixian";         Get-File 804 "zip" "advanced_audio_hailu"
}
$zip = "$out.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path "$out\*.ods" -DestinationPath $zip
Write-Host ""
Write-Host "Done. Send this file to Claude: $zip" -ForegroundColor Green
