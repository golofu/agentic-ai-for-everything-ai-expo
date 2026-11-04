# Record one REAL Claude Desktop run end to end:  .\record-job.ps1 -Slug 236-1 [-RecDir <dir>]
# Needs: Claude Desktop open with the sidebar hidden, scripts\howto\jobs.json (make_jobs.py), win.ps1 helpers.
# Writes <RecDir>\<slug>.mkv (raw screen) and <RecDir>\<slug>.events.json (timestamps for edit.py specs).
param([Parameter(Mandatory)][string]$Slug,
      [string]$RecDir = "C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\rec",
      [string]$Helpers = "C:\Users\User\AppData\Local\Temp\claude\785b8701d42b026f\8724ba23-8dc5-42db-aebc-2ec74bc49f15\scratchpad\desk\win.ps1",
      [int]$MaxWait = 600)
. $Helpers
Add-Type -AssemblyName System.Drawing
$job = (Get-Content (Join-Path $PSScriptRoot "jobs.json") -Raw -Encoding utf8 | ConvertFrom-Json) | Where-Object slug -eq $Slug
if (-not $job) { throw "unknown job $Slug" }
New-Item -ItemType Directory -Force $RecDir | Out-Null
$mkv = Join-Path $RecDir "$Slug.mkv"
$events = [ordered]@{}; $script:dlog = @()
$sw = [Diagnostics.Stopwatch]::new()
function Ev([string]$name) { $events[$name] = [math]::Round($sw.Elapsed.TotalSeconds, 2) }
function Darkness([int]$cx, [int]$cy, [int]$r = 7) {
  $bmp = New-Object Drawing.Bitmap (2 * $r), (2 * $r)
  $g = [Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($cx - $r, $cy - $r, 0, 0, $bmp.Size); $g.Dispose()
  $dark = 0
  for ($x = 0; $x -lt $bmp.Width; $x++) { for ($y = 0; $y -lt $bmp.Height; $y++) { if ($bmp.GetPixel($x, $y).GetBrightness() -lt 0.25) { $dark++ } } }
  $bmp.Dispose(); $dark / (4 * $r * $r)
}
function Running { (Darkness 1412 952) -gt 0.5 }   # reply box shows a solid black stop square while Claude works
function Close-Explorer([string]$path) {
  foreach ($w in (New-Object -ComObject Shell.Application).Windows()) { try { if ($w.Document.Folder.Self.Path -eq $path) { $w.Quit() } } catch {} }
}
function Show-Explorer([string]$path, [int]$secs) {
  Start-Process explorer.exe "`"$path`""; Start-Sleep 2.5
  $h = [IntPtr]::Zero
  foreach ($w in (New-Object -ComObject Shell.Application).Windows()) { try { if ($w.Document.Folder.Self.Path -eq $path) { $h = [IntPtr]$w.HWND } } catch {} }
  if ($h -ne [IntPtr]::Zero) { [W]::ShowWindow($h, 3) | Out-Null; [W]::SetForegroundWindow($h) | Out-Null }
  Start-Sleep $secs
  Close-Explorer $path
}
function Wait-Claude([int]$max) {
  Start-Sleep 8
  $idle = 0; $t = 0; $n = 0
  while ($t -lt $max) {
    $dk = Darkness 1412 952; $script:dlog += "$t=$([math]::Round($dk,2))"; if ($dk -gt 0.3) { $idle = 0 } else { $idle++ }
    if ($idle -ge 3) { return $true }
    if ($t % 30 -eq 0) { $n++; ffmpeg -v error -y -f gdigrab -i desktop -frames:v 1 (Join-Path $RecDir "$Slug-wait$n.png") }
    Start-Sleep 4; $t += 4
  }
  return $false
}

$before = @{}; Get-ChildItem $job.watchPath -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { $before[$_.FullName] = $_.LastWriteTimeUtc }

$ff = Start-Process ffmpeg -ArgumentList "-v error -y -f gdigrab -framerate 20 -draw_mouse 1 -i desktop -vf crop=1920:1028:0:0 -c:v libx264 -preset ultrafast -crf 18 -pix_fmt yuv420p `"$mkv`"" -WindowStyle Hidden -PassThru
Start-Sleep 1.5; $sw.Start(); Ev "start"

# 1) the input files, as the learner would see them
Ev "files"; Show-Explorer $job.showPath 5; Ev "files-end"

# 2) new chat + attach the folder
Focus-App claude; Key "{ESC}"; Start-Sleep 0.3
[W]::keybd_event(0x11,0,0,0); [W]::keybd_event(0x4E,0,0,0); [W]::keybd_event(0x4E,0,2,0); [W]::keybd_event(0x11,0,2,0); Start-Sleep 1.5
Ev "pick"
Click 640 651; Start-Sleep 1.2; Click 640 601; Start-Sleep 2.2
Click 940 669; CtrlA; TypeSlow $job.attachPath 5 35; Start-Sleep 0.6; Enter; Start-Sleep 1.8; Click 1232 707; Start-Sleep 2.5
Ev "allow"; Click 1156 571; Start-Sleep 1.5; Ev "allow-end"

# 3) the prompt
Ev "prompt"; Click 900 530; Start-Sleep 0.3; TypeSlow $job.prompt 6 25; Start-Sleep 1.2
Ev "send"; Enter
$ok = Wait-Claude $MaxWait; Ev ($(if ($ok) { "done" } else { "timeout" }))
foreach ($f in $job.followups) {
  Start-Sleep 2; Ev "followup"; Click 900 952; Start-Sleep 0.3; TypeSlow $f 3 60; Start-Sleep 0.8; Enter
  $ok = Wait-Claude $MaxWait; Ev ($(if ($ok) { "done2" } else { "timeout2" }))
}
Start-Sleep 3; Ev "reply-end"

# 4) the result on disk
$new = Get-ChildItem $job.watchPath -Recurse -File -ErrorAction SilentlyContinue | Where-Object { -not $before.ContainsKey($_.FullName) -or $before[$_.FullName] -ne $_.LastWriteTimeUtc } | Sort-Object LastWriteTime
Ev "result"; Show-Explorer $job.watchPath 5; Ev "result-explorer-end"
$rank = @{ '.docx' = 1; '.xlsx' = 2; '.md' = 3; '.txt' = 4; '.csv' = 5; '.ics' = 6 }; $main = $new | Where-Object { $rank.ContainsKey($_.Extension.ToLower()) } | Sort-Object { $rank[$_.Extension.ToLower()] }, { -$_.LastWriteTime.Ticks } | Select-Object -First 1
if ($main) {
  $ext = $main.Extension.ToLower()
  if ($ext -in '.md', '.txt', '.csv', '.ics') { $p = Start-Process notepad.exe "`"$($main.FullName)`"" -PassThru } else { Invoke-Item $main.FullName }
  Start-Sleep 8; Ev "open"
  Start-Sleep 7
  $fg = Get-Process | Where-Object { $_.MainWindowTitle -like "*$($main.BaseName)*" } | Select-Object -First 1
  if ($fg) { [W]::SetForegroundWindow($fg.MainWindowHandle) | Out-Null; Start-Sleep 0.3; [W]::keybd_event(0x12,0,0,0); [W]::keybd_event(0x73,0,0,0); [W]::keybd_event(0x73,0,2,0); [W]::keybd_event(0x12,0,2,0) }
}
Start-Sleep 1; Ev "end"
Stop-Process -Id $ff.Id; Start-Sleep 1
$events["darkness"] = $script:dlog -join " "; $events["newFiles"] = @($new | ForEach-Object { $_.FullName })
$events["mainFile"] = $(if ($main) { $main.FullName } else { $null })
[IO.File]::WriteAllText((Join-Path $RecDir "$Slug.events.json"), ($events | ConvertTo-Json -Depth 4), (New-Object Text.UTF8Encoding $false))
ffmpeg -v error -y -i $mkv -c copy (Join-Path $RecDir "$Slug-fixed.mkv") 2>$null
Focus-App claude; Key "{ESC}"
"$Slug ok=$ok new=$(@($new).Count) main=$($main.Name)"
