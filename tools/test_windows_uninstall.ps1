# Maintainer test for the Windows uninstall logic (release_files/windows/app/uninstall.ps1).
#
# It DOT-SOURCES the real uninstall.ps1 and tests the function it defines, so this cannot drift
# from what ships. Dot-sourcing that file only defines the function; it performs no uninstall.
#
# SAFE TO RUN ON ANY WINDOWS MACHINE. It installs nothing. It creates and deletes files only
# inside a new folder under the temp directory, and it never touches the real Desktop, the
# Startup folder, the registry, or any scheduled task.
#
#   powershell -ExecutionPolicy Bypass -File test_windows_uninstall.ps1
#
# It also runs under PowerShell 7 on Linux, so it can be run in a throwaway container.

param([string]$UninstallScript)

$ErrorActionPreference = 'Stop'
# %TEMP% on Windows; GetTempPath() also covers PowerShell on Linux, so this can be run in a
# throwaway container as well as on a real Windows box.
$TempBase = if ($env:TEMP) { $env:TEMP } else { [System.IO.Path]::GetTempPath() }
$Root = Join-Path $TempBase ('woty-uninstall-test-' + [guid]::NewGuid().ToString('N').Substring(0,8))
Write-Host "Sandbox: $Root"
Write-Host ''

if (-not $UninstallScript) {
    foreach ($c in @((Join-Path $PSScriptRoot 'uninstall.ps1'),
                     (Join-Path $PSScriptRoot 'release_files/windows/app/uninstall.ps1'))) {
        if (Test-Path $c -PathType Leaf) { $UninstallScript = $c; break }
    }
}
if (-not ($UninstallScript -and (Test-Path $UninstallScript -PathType Leaf))) {
    Write-Host 'FAIL: could not find uninstall.ps1 - pass -UninstallScript <path>'; exit 2
}
Write-Host "Testing: $UninstallScript"

$marker = Join-Path $Root 'main-body-ran.txt'
. $UninstallScript
if (-not (Get-Command Remove-WotyDesktopFolder -ErrorAction SilentlyContinue)) {
    Write-Host 'FAIL: dot-sourcing uninstall.ps1 did not define Remove-WotyDesktopFolder'; exit 2
}
Write-Host 'pass  0: dot-sourcing defines the function and runs no uninstall'
Write-Host ''

function New-Layout {
    param([string]$Base, [switch]$WithUserFiles)
    $Folder = Join-Path $Base 'Wheel of the Year'
    $Pics   = Join-Path $Folder 'Pictures'
    New-Item -ItemType Directory -Path $Pics -Force | Out-Null
    foreach ($n in @('Backgrounds.lnk','Wedges.lnk','Sabbat ring.lnk','Centre.lnk','Ring symbols.lnk')) {
        Set-Content -LiteralPath (Join-Path $Pics $n) -Value 'pretend shortcut'
    }
    foreach ($n in @('Settings.lnk','Update Wallpaper Now.lnk','Program folder.lnk','Pictures.lnk')) {
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

$fail = 0

# 1. Nothing of the user's in there: the whole folder should go.
$f1 = New-Layout -Base (Join-Path $Root 't1')
Remove-WotyDesktopFolder -Folder $f1
if (Test-Path $f1) { Write-Host 'FAIL  1: a clean folder was left behind'; $fail++ }
else              { Write-Host 'pass  1: clean folder removed entirely' }

# 2. The user put their own things in there: those must survive, ours must go.
$f2 = New-Layout -Base (Join-Path $Root 't2') -WithUserFiles
Remove-WotyDesktopFolder -Folder $f2
$notes = Join-Path $f2 'my notes.txt'
$altar = Join-Path (Join-Path (Join-Path $f2 'Pictures') 'My Favourites') 'altar.jpg'
if      (-not (Test-Path $notes))              { Write-Host 'FAIL  2: the user note was deleted'; $fail++ }
elseif  (-not (Test-Path $altar))              { Write-Host 'FAIL  2: the user picture was deleted'; $fail++ }
elseif  (Test-Path (Join-Path $f2 'Settings.lnk')) { Write-Host 'FAIL  2: our shortcut was left behind'; $fail++ }
else    { Write-Host 'pass  2: user files kept, our shortcuts removed, folder kept' }

# 3. desktop.ini is Windows' own file and must not keep the folder alive.
$f3 = New-Layout -Base (Join-Path $Root 't3')
Set-Content -LiteralPath (Join-Path $f3 'desktop.ini') -Value '[.ShellClassInfo]'
Remove-WotyDesktopFolder -Folder $f3
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
