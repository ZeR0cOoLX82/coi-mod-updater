# COI-Extended Mod Updater

[![Read in English](https://img.shields.io/badge/Language-English-blue.svg)](README.md)

Automatischer Mod-Updater für **Captain of Industry** (COI-Extended Mod Pack).

## Features
- ✅ Automatische Update-Erkennung via GitHub API
- ✅ SHA256-Verifikation jedes Downloads
- ✅ Automatische Backups vor jedem Update (max. 3 pro Mod)
- ✅ Rollback-Funktion auf jede vorherige Version
- ✅ System-Tray Integration mit animiertem Icon
- ✅ Animiertes Tray-Icon während Updates
- ✅ Wartungsfenster (Updates nur zu bestimmten Uhrzeiten)
- ✅ Windows Autostart-Unterstützung
- ✅ Mehrsprachig (Deutsch / Englisch, automatische Erkennung)
- ✅ Dark/Light Theme
- ✅ Konfigurierbare Schriftgröße (7–14pt)
- ✅ Farbiger Log-Viewer mit Filter
- ✅ Dashboard mit Mod-Status & Festplattennutzung

## Installation

### Als Python Script
```bash
pip install -r requirements.txt
python coi_mod_updater.py
```

### Als .exe (Standalone)
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon="coi_updater.ico" --name "COI-Mod-Updater" coi_mod_updater.py
```

## Datenpfade
| Datei | Pfad |
|-------|------|
| Settings | `%APPDATA%\COIModUpdater\settings.json` |
| Cache | `%APPDATA%\COIModUpdater\coi_mod_versions.json` |
| Log | `%APPDATA%\COIModUpdater\coi_updater.log` |
| Backups | `%APPDATA%\COIModUpdater\backups\` |

## Unterstützte Mods
- COIExtended.Automation
- COIExtended.Cheats
- COIExtended.Core
- COIExtended.Difficulty
- COIExtended.ItemSink
- COIExtended.RecipeMaker
- COIExtended.StoragePlus
- COIExtended.Tweaks

## Ordnerstruktur
```
📁 COIModUpdater/          ← .exe liegt hier
└── coi_updater.ico        ← Icon (neben der .exe)

📁 %APPDATA%\COIModUpdater\
├── settings.json
├── coi_mod_versions.json
├── coi_updater.log
└── 📁 backups\
    └── 📁 COIExtended.Core\
        └── COIExtended.Core_v1.5_20260318_143022.zip
```

## Einstellungen
| Option | Beschreibung | Standard |
|--------|-------------|---------|
| GitHub Token | Für höhere API Rate-Limits | leer |
| Check Interval | Stunden zwischen Checks | 3h |
| Mods Folder | Pfad zum Mods-Ordner | Auto |
| Max Backups | Backups pro Mod | 3 |
| SHA256 Verify | Hash-Prüfung nach Download | An |
| Maintenance Window | Update-Zeitfenster | Aus |
| Theme | Dark / Light | Dark |
| Sprache | DE / EN / Auto | Auto |

## Bekannte Anforderungen
- Windows 10/11
- Python 3.10+ (wenn als Script)
- Internetverbindung für GitHub API

## Credits
- Entwickelt von **ZeR0cOoLX82**
- Mods von [Keranik/COI-Extended](https://github.com/Keranik/COI-Extended)
