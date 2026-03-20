# Changelog

[![Auf Deutsch lesen](https://img.shields.io/badge/Language-Deutsch-blue.svg)](CHANGELOG.de.md)

## v1.0.0 – 2026-03-20
### Initial Release
- Automatic update detection
- SHA256 verification
- Backup & Rollback system
- System-Tray integration
- Animated tray icon
- Bilingual (EN/DE)
- Dark/Light Theme
- Maintenance window
- Windows Startup support
- Dashboard
- Colored log viewer

### Stability Fixes (Dry-Run verified)
- Fix #1: Zombie threads in _minimize()
- Fix #2: Zombie threads in Settings standalone
- Fix #3: Missing error popup without internet correlation
- Fix #4: TclError in Tooltip._show()
- Fix #5: Data loss with corrupted backups
- Fix #6: Temp folder leftovers in extract_zip()
- Fix #7: ZeroDivisionError in ETA calculation
- Fix #8: JSONDecodeError with corrupted cache file
