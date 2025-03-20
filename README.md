# Modrinth Profile To Server-side Modlist
![GUI](https://github.com/Flxrd/ModrinthProfileToServer/blob/main/repores/ProfileSelection.png?raw=true)

## Features
- **Database Query:** Reads the Modrinth app's SQLite database for available profiles.
- **Mod Processing:** Opens each mod's `.jar` file in a selected profile, extracts the mod ID from `META-INF/mods.toml`.
- **API Search:** Searches the Modrinth API for each mod.

## Requirements
- [Python 3.6+](https://www.python.org/downloads/)
### These are install automatically if not present.
- [customtkinter](https://pypi.org/project/customtkinter/)
- [requests](https://pypi.org/project/requests/)
- [Pillow](https://pypi.org/project/Pillow/)
