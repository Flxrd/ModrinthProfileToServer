# Modrinth Profile To Server-side Modlist
![GUI](https://github.com/Flxrd/ModrinthProfileToServer/blob/main/repores/ProfileSelection.png?raw=true)

## Features
- **Forge Only:** as of right now this script only supports forge modpacks.
- **Database Query:** Reads the Modrinth app's SQLite database for available profiles.
- **Mod Processing:** Opens each mod's `.jar` file in a selected profile, extracts the mod ID from `META-INF/mods.toml`.
- **API Search:** Searches the Modrinth API for each mod.

## Requirements
- [Python 3.6+](https://www.python.org/downloads/)
### These are install automatically if not present.
- [customtkinter](https://pypi.org/project/customtkinter/)
- [requests](https://pypi.org/project/requests/)
- [Pillow](https://pypi.org/project/Pillow/)

## Installation
- Download and unzip the file from [Releases](https://github.com/Flxrd/ModrinthProfileToServer/releases)
- Open a terminal and run python master.py
- A profile selection screen will appear for you to select your profile (only select forge profiles)
- The GUI may freeze and become unresponsive, the script is still running (check the terminal)
- your files will appear in "exports/(profilename)"
