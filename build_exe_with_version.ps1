$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = "C:/Program Files (x86)/Microsoft Visual Studio/Shared/Python39_64/python.exe"
$mainScript = Join-Path $projectRoot 'coi_mod_updater.py'
$iconPath = Join-Path $projectRoot 'assets\keranik_updater_icon.ico'
$versionInfo = Join-Path $projectRoot 'version_info.txt'
$distPath = Join-Path $projectRoot 'dist'
$buildPath = Join-Path $projectRoot 'build'
$specPath = Join-Path $projectRoot 'COI-Mod-Updater.spec'

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found: $pythonExe"
}

if (-not (Test-Path $iconPath)) {
    throw "ICO file not found: $iconPath"
}

if (-not (Test-Path $versionInfo)) {
    throw "Version info file not found: $versionInfo"
}

& $pythonExe -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller is not installed for this Python environment.'
}

# Write version info as a .rc file
$rcPath = Join-Path $projectRoot 'coi_mod_updater_version.rc'
$exeName = 'COI-Mod-Updater.exe'
$versionLines = Get-Content $versionInfo | Where-Object { $_ -notmatch '^#' -and $_ -ne '' }
$rcContent = '@"1 VERSIONINFO
FILEVERSION 1,0,0,0
PRODUCTVERSION 1,0,0,0
BEGIN
'
foreach ($line in $versionLines) {
    $parts = $line -split '='
    if ($parts.Length -eq 2) {
        $rcContent += '    VALUE "' + $parts[0] + '", "' + $parts[1] + '"\n'
    }
}
$rcContent += 'END'
Set-Content -Path $rcPath -Value $rcContent

# Compile .rc to .res using windres (if available)
$windres = 'windres.exe'
$resPath = Join-Path $projectRoot 'coi_mod_updater_version.res'
if (Get-Command $windres -ErrorAction SilentlyContinue) {
    & $windres -i $rcPath -o $resPath
    if ($LASTEXITCODE -ne 0) {
        throw 'windres failed to compile version resource.'
    }
    $versionOpt = "--version-file $resPath"
} else {
    Write-Warning 'windres not found, version info will not be embedded.'
    $versionOpt = ''
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
    $versionOpt `
    $mainScript

if ($LASTEXITCODE -ne 0) {
    throw 'PyInstaller build failed.'
}

Write-Host "Build complete: $(Join-Path $distPath $exeName)"
Write-Host "Spec file: $specPath"
