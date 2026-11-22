# Maintainer test for the Windows uninstall logic (release_files/windows/app/uninstall.ps1).
#
# SAFE TO RUN ON ANY WINDOWS MACHINE. It installs nothing. It creates and deletes files only
# inside a new folder under %TEMP%, and it never touches the real Desktop, the Startup folder,
# the registry, or any scheduled task.
#
# NOTE: the cleanup block below is a COPY of the one in uninstall.ps1. If you change the real
# script, change this one to match - otherwise this tests code that no longer ships.
#
#   powershell -ExecutionPolicy Bypass -File test_windows_uninstall.ps1

$ErrorActionPreference = 'Stop'
$Root = Join-Path $env:TEMP ('woty-uninstall-test-' + [guid]::NewGuid().ToString('N').Substring(0,8))
Write-Host "Sandbox: $Root"
Write-Host ''

function New-Layout {
    param([string]$Base, [switch]$WithUserFiles)
    $Folder = Join-Path $Base 'Wheel of the Year'
    $Pics   = Join-Path $Folder 'Pictures'
    New-Item -ItemType Directory -Path $Pics -Force | Out-Null
    foreach ($n in @('Backgrounds.lnk','Wedges.lnk','Sabbat ring.lnk','Centre.lnk')) {
        Set-Content -LiteralPath (Join-Path $Pics $n) -Value 'pretend shortcut'
    }
    foreach ($n in @('Settings.lnk','Update Wallpaper Now.lnk','Program folder.lnk')) {
        Set-Content -LiteralPath (Join-Path $Folder $n) -Value 'pretend shortcut'
    }
    if ($WithUserFiles) {
        Set-Content -LiteralPath (Join-Path $Folder 'my notes.txt') -Value 'mine'
        $own = Join-Path $Pics 'My Favourites'
        New-Item -ItemType Directory -Path $own -Force | Out-Null
        Set-Content -LiteralPath (Join-Path $own 'altar.jpg') -Value 'mine'
    }
    return $Folder
}

# --- the block under test, copied from uninstall.ps1 (1.1.1 onwards) ---
function Invoke-Cleanup {
    param([string]$Folder)
    $Pics = Join-Path $Folder 'Pictures'
    foreach ($n in @('Backgrounds.lnk', 'Wedges.lnk', 'Sabbat ring.lnk', 'Centre.lnk',
                     'Ring symbols.lnk')) {
        $f = Join-Path $Pics $n
        if (Test-Path $f -PathType Leaf) { Remove-Item $f }
    }
    foreach ($n in @('Settings.lnk', 'Update Wallpaper Now.lnk', 'Program folder.lnk',
                     'Pictures.lnk')) {
        $f = Join-Path $Folder $n
        if (Test-Path $f -PathType Leaf) { Remove-Item $f }
    }
    foreach ($d in @($Pics, $Folder)) {
        if (Test-Path $d -PathType Container) {
            $left = @(Get-ChildItem -LiteralPath $d -Force | Where-Object { $_.Name -ne 'desktop.ini' })
            if ($left.Count -eq 0) { Remove-Item $d -Recurse -Force }
        }
    }
}

$fail = 0

# 1. Nothing of the user's in there: the whole folder should go.
$f1 = New-Layout -Base (Join-Path $Root 't1')
Invoke-Cleanup -Folder $f1
if (Test-Path $f1) { Write-Host 'FAIL  1: a clean folder was left behind'; $fail++ }
else              { Write-Host 'pass  1: clean folder removed entirely' }

# 2. The user put their own things in there: those must survive, ours must go.
$f2 = New-Layout -Base (Join-Path $Root 't2') -WithUserFiles
Invoke-Cleanup -Folder $f2
$notes = Join-Path $f2 'my notes.txt'
$altar = Join-Path (Join-Path (Join-Path $f2 'Pictures') 'My Favourites') 'altar.jpg'
if      (-not (Test-Path $notes))              { Write-Host 'FAIL  2: the user note was deleted'; $fail++ }
elseif  (-not (Test-Path $altar))              { Write-Host 'FAIL  2: the user picture was deleted'; $fail++ }
elseif  (Test-Path (Join-Path $f2 'Settings.lnk')) { Write-Host 'FAIL  2: our shortcut was left behind'; $fail++ }
else    { Write-Host 'pass  2: user files kept, our shortcuts removed, folder kept' }

# 3. desktop.ini is Windows' own file and must not keep the folder alive.
$f3 = New-Layout -Base (Join-Path $Root 't3')
Set-Content -LiteralPath (Join-Path $f3 'desktop.ini') -Value '[.ShellClassInfo]'
Invoke-Cleanup -Folder $f3
if (Test-Path $f3) { Write-Host 'FAIL  3: desktop.ini stopped the folder being removed'; $fail++ }
else              { Write-Host 'pass  3: desktop.ini ignored, folder removed' }

# 4. For comparison: what the pre-1.1.1 line did to the same layout.
$f4 = New-Layout -Base (Join-Path $Root 't4') -WithUserFiles
Remove-Item $f4 -Recurse -Force
if (Test-Path (Join-Path $f4 'my notes.txt')) {
    Write-Host 'note  4: the old code kept the note - unexpected, say so'
} else {
    Write-Host 'note  4: the old code deleted the user note - that is the bug 1.1.1 fixed'
}

Write-Host ''
if ($fail -eq 0) { Write-Host 'ALL TESTS PASSED' } else { Write-Host "$fail TEST(S) FAILED" }
Remove-Item $Root -Recurse -Force
Write-Host "Sandbox removed: $Root"
