# Wheel of the Year wallpaper - Windows installer (run via "Install.cmd").
# Registers a Task Scheduler task for the current user: daily at 00:01, catching up if the PC
# was off, plus at log-on. No administrator rights needed.
$ErrorActionPreference = 'Stop'
$App    = Split-Path -Parent $MyInvocation.MyCommand.Path
$Pyw    = Join-Path $App 'python\pythonw.exe'
$Script = Join-Path $App 'wheel-of-the-year.py'
$Name   = 'Wheel of the Year Wallpaper'
$Startup = Join-Path ([Environment]::GetFolderPath('Startup')) "$Name.lnk"

if (-not (Test-Path $Pyw)) { throw "Can't find $Pyw - please unzip the whole folder first." }

# First install: start from the default settings. Later updates keep the ones you have.
$Root0 = Split-Path -Parent $App
if (-not (Test-Path (Join-Path $Root0 'config.toml'))) {
    Copy-Item (Join-Path $Root0 'config.default.toml') (Join-Path $Root0 'config.toml')
}

$action   = New-ScheduledTaskAction -Execute $Pyw -Argument "`"$Script`"" -WorkingDirectory $App
$daily    = New-ScheduledTaskTrigger -Daily -At '00:01'
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
$desc     = 'Redraws the Wheel of the Year desktop wallpaper each day.'

try {
    $logon = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
    Register-ScheduledTask -TaskName $Name -Action $action -Trigger @($daily, $logon) `
        -Settings $settings -Description $desc -Force | Out-Null
    if (Test-Path $Startup) { Remove-Item $Startup }
} catch {
    # Some Windows setups only allow log-on tasks for administrators: use the Startup folder instead.
    Register-ScheduledTask -TaskName $Name -Action $action -Trigger $daily `
        -Settings $settings -Description $desc -Force | Out-Null
    $ws  = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($Startup)
    $lnk.TargetPath = $Pyw; $lnk.Arguments = "`"$Script`""; $lnk.WorkingDirectory = $App
    $lnk.Save()
}

# A Settings shortcut with a gear icon, opening config.toml in Notepad.
$Root = Split-Path -Parent $App
$ws   = New-Object -ComObject WScript.Shell
$set  = $ws.CreateShortcut((Join-Path $Root 'Settings.lnk'))
$set.TargetPath       = "$env:WINDIR\system32\notepad.exe"
$set.Arguments        = "`"$(Join-Path $Root 'config.toml')`""
$set.WorkingDirectory = $Root
$set.IconLocation     = Join-Path $App 'assets\icons\settings.ico'
$set.Description      = 'Change how the Wheel of the Year wallpaper looks'
$set.Save()

# One folder on the desktop holding all three shortcuts, so everything is in the same place.
$Folder = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Wheel of the Year'
New-Item -ItemType Directory -Path $Folder -Force | Out-Null

$d = $ws.CreateShortcut((Join-Path $Folder 'Settings.lnk'))
$d.TargetPath = $set.TargetPath; $d.Arguments = $set.Arguments
$d.WorkingDirectory = $Root; $d.IconLocation = $set.IconLocation
$d.Description = $set.Description
$d.Save()

$upd = $ws.CreateShortcut((Join-Path $Folder 'Update Wallpaper Now.lnk'))
$upd.TargetPath       = Join-Path $Root 'Update Wallpaper Now.cmd'
$upd.WorkingDirectory = $Root
$upd.IconLocation     = Join-Path $App 'assets\icons\update.ico'
$upd.Description      = "Redraw today's wallpaper with your latest pictures and settings"
$upd.Save()

$pics = $ws.CreateShortcut((Join-Path $Folder 'Pictures.lnk'))
$pics.TargetPath   = Join-Path $Root 'backgrounds'
$pics.Description  = 'The folders the wallpaper reads: backgrounds, wedges, sabbat-ring, centre'
$pics.Save()

# tidy away loose icons older versions left on the desktop
foreach ($old in @('Wheel of the Year Settings.lnk', 'Wheel of the Year Update Now.lnk')) {
    $f = Join-Path ([Environment]::GetFolderPath('Desktop')) $old
    if (Test-Path $f) { Remove-Item $f }
}

Write-Host 'Drawing today''s wallpaper...'
Start-Process -FilePath $Pyw -ArgumentList "`"$Script`"" -WorkingDirectory $App -Wait
$log = Join-Path (Split-Path -Parent $App) 'build\log.txt'
if (Test-Path $log) { Get-Content $log -Tail 3 }
Write-Host ''
Write-Host 'Wheel of the Year @VERSION@'
Write-Host 'Installed. The wallpaper now refreshes every night at 00:01 and when you log in.'
Write-Host 'If you move this folder, run Install again.'
Write-Host 'On your desktop there is now a "Wheel of the Year" folder holding Settings,'
Write-Host 'Update Wallpaper Now, and Pictures (the folders it reads).'
