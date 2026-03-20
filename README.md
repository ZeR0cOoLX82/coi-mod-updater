# COI-Extended Mod Updater

[![Auf Deutsch lesen](https://img.shields.io/badge/Language-Deutsch-blue.svg)](README.de.md)

Automatic mod updater for **Captain of Industry** (COI-Extended Mod Pack).

## Features
- ✅ Automatic update detection via GitHub API
- ✅ SHA256 verification of every download
- ✅ Automatic backups before every update (max 3 per mod)
- ✅ Rollback function to restore any previous version
- ✅ System-Tray integration with animated icon
- ✅ Animated tray icon during updates
- ✅ Maintenance window (updates only during allowed hours)
- ✅ Windows startup support
- ✅ Multilingual (Auto-detects English / German)
- ✅ Dark/Light Theme
- ✅ Configurable font size (7–14pt)
- ✅ Colored log viewer with filtering
- ✅ Dashboard showing mod status & disk usage

## Installation

### As Python Script
```bash
pip install -r requirements.txt
python coi_mod_updater.py
```

### As .exe (Standalone)
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon="coi_updater.ico" --name "COI-Mod-Updater" coi_mod_updater.py
```

## Data Paths
| File | Path |
|-------|------|
| Settings | `%APPDATA%\COIModUpdater\settings.json` |
| Cache | `%APPDATA%\COIModUpdater\coi_mod_versions.json` |
| Log | `%APPDATA%\COIModUpdater\coi_updater.log` |
| Backups | `%APPDATA%\COIModUpdater\backups\` |

## Supported Mods
- COIExtended.Automation
- COIExtended.Cheats
- COIExtended.Core
- COIExtended.Difficulty
- COIExtended.ItemSink
- COIExtended.RecipeMaker
- COIExtended.StoragePlus
- COIExtended.Tweaks

## Directory Structure
```
📁 COIModUpdater/          ← .exe is located here
└── coi_updater.ico        ← Icon (next to .exe)

📁 %APPDATA%\COIModUpdater\
├── settings.json
├── coi_mod_versions.json
├── coi_updater.log
└── 📁 backups\
    └── 📁 COIExtended.Core\
        └── COIExtended.Core_v1.5_20260318_143022.zip
```

## Settings
| Option | Description | Default |
|--------|-------------|---------|
| GitHub Token | For higher API rate limits | empty |
| Check Interval | Hours between update checks | 3h |
| Mods Folder | Path to the mods directory | Auto |
| Max Backups | Limit of backups per mod | 3 |
| SHA256 Verify | Integrity check after download | On |
| Maintenance Window | Allow updates only in this timeframe | Off |
| Theme | Dark / Light | Dark |
| Language | EN / DE / Auto | Auto |

## Requirements
- Windows 10/11
- Python 3.10+ (if running as script)
- Internet connection for GitHub API

## Credits
- Developed by **ZeR0cOoLX82**
- Mods by [Keranik/COI-Extended](https://github.com/Keranik/COI-Extended)
