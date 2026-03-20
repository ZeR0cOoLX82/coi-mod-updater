$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "C:/Program Files (x86)/Microsoft Visual Studio/Shared/Python39_64/python.exe"
$mainScript = Join-Path $projectRoot 'coi_mod_updater.py'
$iconPath = Join-Path $projectRoot 'assets\keranik_updater_icon.ico'
$distPath = Join-Path $projectRoot 'dist'
$buildPath = Join-Path $projectRoot 'build'
$specPath = Join-Path $projectRoot 'COI-Mod-Updater.spec'

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found: $pythonExe"
}

if (-not (Test-Path $iconPath)) {
    throw "ICO file not found: $iconPath"
}

& $pythonExe -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller is not installed for this Python environment.'
}

& $pythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name 'COI-Mod-Updater' `
    --icon $iconPath `
    --add-data "$iconPath;assets" `
    --distpath $distPath `
    --workpath $buildPath `
    --specpath $projectRoot `
    $mainScript

if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller build failed.'
}

Write-Host "Build complete: $(Join-Path $distPath 'COI-Mod-Updater.exe')"
Write-Host "Spec file: $specPath"
