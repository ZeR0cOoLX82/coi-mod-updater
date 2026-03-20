# Changelog

## v1.0.0 – 2026-03-20
### Initiales Release
- Automatische Update-Erkennung
- SHA256-Verifikation
- Backup & Rollback System
- System-Tray Integration
- Animiertes Tray-Icon
- Mehrsprachigkeit (DE/EN)
- Dark/Light Theme
- Wartungsfenster
- Windows Autostart
- Dashboard
- Farbiger Log-Viewer

### Stability Fixes (Dry-Run verified)
- Fix #1: Zombie-Threads bei _minimize()
- Fix #2: Zombie-Threads bei Settings-Standalone
- Fix #3: Fehlermeldung bei fehlendem Internet
- Fix #4: TclError in Tooltip._show()
- Fix #5: Datenverlust bei korrupten Backups
- Fix #6: Temp-Ordner Leichen in extract_zip()
- Fix #7: ZeroDivisionError bei ETA-Berechnung
- Fix #8: JSONDecodeError bei korrupter Cache-Datei
