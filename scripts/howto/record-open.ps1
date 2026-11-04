# Record only "open the real output file" for a job whose main clip missed it (Word slow to start, etc.)
# .\record-open.ps1 -Slug 240-6   -> <RecDir>\<slug>-open.mkv + <slug>-open.events.json
param([Parameter(Mandatory)][string]$Slug,
      [string]$RecDir = "C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\rec",
      [string]$Helpers = "C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\desk\win.ps1")
. $Helpers
$ev = Get-Content (Join-Path $RecDir "$Slug.events.json") -Raw -Encoding utf8 | ConvertFrom-Json
$file = Get-Item $ev.mainFile
$mkv = Join-Path $RecDir "$Slug-open.mkv"
$ff = Start-Process ffmpeg -ArgumentList "-v error -y -f gdigrab -framerate 20 -draw_mouse 1 -i desktop -vf crop=1920:1028:0:0 -c:v libx264 -preset ultrafast -crf 18 -pix_fmt yuv420p `"$mkv`"" -WindowStyle Hidden -PassThru
for ($i = 0; $i -lt 40 -and -not ((Test-Path $mkv) -and (Get-Item $mkv).Length -gt 200000); $i++) { Start-Sleep -Milliseconds 500 }; Start-Sleep 1; $sw = [Diagnostics.Stopwatch]::StartNew()
Invoke-Item $file.FullName
$shown = $null
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 500
  $p = Get-Process WINWORD, EXCEL -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*$($file.BaseName)*" } | Select-Object -First 1
  if ($p) { [W]::ShowWindow($p.MainWindowHandle, 3) | Out-Null; [W]::SetForegroundWindow($p.MainWindowHandle) | Out-Null; Start-Sleep 2.5; $shown = [math]::Round($sw.Elapsed.TotalSeconds, 2); break }
}
Start-Sleep 8; $end = [math]::Round($sw.Elapsed.TotalSeconds, 2)
if ($p) { $p.CloseMainWindow() | Out-Null; Start-Sleep 3 }
Stop-Process -Id $ff.Id; Start-Sleep 1
ffmpeg -v error -y -i $mkv -c copy (Join-Path $RecDir "$Slug-open-fixed.mkv") 2>$null
[IO.File]::WriteAllText((Join-Path $RecDir "$Slug-open.events.json"), (@{ shown = $shown; end = $end } | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
Focus-App claude; Key "{ESC}"
"$Slug open shown=$shown end=$end"
