# Wheel of the Year wallpaper - stop the daily refresh (run via "Uninstall.cmd").
$Name = 'Wheel of the Year Wallpaper'
Unregister-ScheduledTask -TaskName $Name -Confirm:$false -ErrorAction SilentlyContinue
$Startup = Join-Path ([Environment]::GetFolderPath('Startup')) "$Name.lnk"
if (Test-Path $Startup) { Remove-Item $Startup }
$Settings = Join-Path (Split-Path -Parent $PSScriptRoot) 'Settings.lnk'
if (Test-Path $Settings) { Remove-Item $Settings }
$Folder = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Wheel of the Year'
if (Test-Path $Folder) { Remove-Item $Folder -Recurse -Force }
foreach ($n in @('Wheel of the Year Settings.lnk', 'Wheel of the Year Update Now.lnk')) {
    $f = Join-Path ([Environment]::GetFolderPath('Desktop')) $n
    if (Test-Path $f) { Remove-Item $f }
}
Write-Host 'Removed. Your current wallpaper stays until you choose another one in Settings > Personalization.'
Write-Host 'You can now delete this folder if you like.'
