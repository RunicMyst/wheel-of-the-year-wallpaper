# Wheel of the Year wallpaper - stop the daily refresh (run via "Uninstall.cmd").
#
# The desktop-folder cleanup is a function so that tools/test_windows_uninstall.ps1 can
# dot-source this file and test the real thing rather than a copy of it. Dot-sourcing defines
# the function without running anything; the work below only happens when the file is run.

function Remove-WotyDesktopFolder {
    # Remove only the shortcuts we made, by name. Anything of your own that you put in this
    # folder is left alone, and the folders themselves only go if that leaves them empty.
    # (Until 1.1.1 this deleted the whole folder and everything in it.)
    param([Parameter(Mandatory=$true)][string]$Folder)

    $Pics = Join-Path $Folder 'Pictures'
    foreach ($n in @('Backgrounds.lnk', 'Wedges.lnk', 'Sabbat ring.lnk', 'Centre.lnk',
                     'Ring symbols.lnk')) {
        $f = Join-Path $Pics $n
        if (Test-Path $f -PathType Leaf) { Remove-Item $f -Force }
    }
    foreach ($n in @('Settings.lnk', 'Update Wallpaper Now.lnk', 'Program folder.lnk',
                     'Pictures.lnk')) {
        $f = Join-Path $Folder $n
        if (Test-Path $f -PathType Leaf) { Remove-Item $f -Force }
    }
    # desktop.ini is Windows' own folder-view file, not something of yours, so it doesn't count.
    foreach ($d in @($Pics, $Folder)) {
        if (Test-Path $d -PathType Container) {
            $left = @(Get-ChildItem -LiteralPath $d -Force | Where-Object { $_.Name -ne 'desktop.ini' })
            if ($left.Count -eq 0) { Remove-Item $d -Recurse -Force }
        }
    }
}

# Dot-sourced (". uninstall.ps1") just defines the function above and stops here.
if ($MyInvocation.InvocationName -eq '.') { return }

$Name = 'Wheel of the Year Wallpaper'
Unregister-ScheduledTask -TaskName $Name -Confirm:$false -ErrorAction SilentlyContinue
$Startup = Join-Path ([Environment]::GetFolderPath('Startup')) "$Name.lnk"
if (Test-Path $Startup) { Remove-Item $Startup -Force }
$Settings = Join-Path (Split-Path -Parent $PSScriptRoot) 'Settings.lnk'
if (Test-Path $Settings) { Remove-Item $Settings -Force }

Remove-WotyDesktopFolder -Folder (Join-Path ([Environment]::GetFolderPath('Desktop')) 'Wheel of the Year')

foreach ($n in @('Wheel of the Year Settings.lnk', 'Wheel of the Year Update Now.lnk')) {
    $f = Join-Path ([Environment]::GetFolderPath('Desktop')) $n
    if (Test-Path $f) { Remove-Item $f -Force }
}
Write-Host 'Removed. Your current wallpaper stays until you choose another one in Settings > Personalization.'
Write-Host 'You can now delete this folder if you like.'
