import os
import json
import sqlite3
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox, Scrollbar, Canvas
from datetime import datetime
import zipfile
import re
import shutil

# Constants
DEFAULT_PATH = os.path.join(os.getenv('APPDATA'), 'ModrinthApp')
DB_FILENAME = 'app.db'
CONFIG_FILE = 'config.json'

# Convert Unix timestamp to relative time
def format_relative_time(timestamp):
    now = datetime.now()
    dt = datetime.fromtimestamp(timestamp)
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"

# Check for Modrinth database
def check_db():
    db_path = os.path.join(DEFAULT_PATH, DB_FILENAME)
    if not os.path.exists(db_path):
        messagebox.showwarning("Database not found", "Failed to locate app.db, please select your ModrinthApp folder.")
        folder_selected = filedialog.askdirectory(title="Select your ModrinthApp folder")

        if folder_selected:
            db_path = os.path.join(folder_selected, DB_FILENAME)
            if not os.path.exists(db_path):
                messagebox.showerror("Error", "app.db was not found in the selected folder")
                return None
        else:
            return None
    return db_path  

# Get profile data from database
def get_profiles(db_path):
    profiles = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, game_version, mod_loader, modified FROM profiles")
        profiles = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to query profiles: {e}")
    return profiles

# process that bitch
def process_mods_in_profile(profile):
    profile_folder = os.path.join(DEFAULT_PATH, "profiles", profile["path"])
    mods_folder = os.path.join(profile_folder, "mods")
    if not os.path.exists(mods_folder):
        messagebox.showerror("Error", f"Mods folder not found in profile {profile['name']}")
        return
    mod_ids = []
    for file in os.listdir(mods_folder):
        if file.endswith(".jar"):
            jar_path = os.path.join(mods_folder, file)
            try:
                with zipfile.ZipFile(jar_path, 'r') as jar:
                    if "META-INF/mods.toml" in jar.namelist():
                        with jar.open("META-INF/mods.toml") as toml_file:
                            content = toml_file.read().decode("utf-8")
                            match = re.search(r'modId\s*=\s*"([^"]+)"', content)
                            if match:
                                mod_id = match.group(1)
                                mod_ids.append({"mod_id": mod_id, "file": file})
                                print(f"Found modId: {mod_id} in {file}")
                            else:
                                print(f"modId not found in {file}")
                    else:
                        print(f"mods.toml not found in {file}")
            except Exception as e:
                print(f"Error processing {file}: {e}")
    if mod_ids:
        mod_info_list = []
        for entry in mod_ids:
            mod_id = entry["mod_id"]
            file_name = entry["file"]
            info = search_mod(mod_id)
            if info and info.get("server_side") in ["required", "optional"]:
                info["file"] = file_name
                mod_info_list.append(info)
        if mod_info_list:
            output_lines = []
            for info in mod_info_list:
                output_lines.append(f"{info['title']} ({info['server_side']}) - Source File: {info['file']}")
            copy_mod_files(profile, mod_info_list)
        else:
            messagebox.showinfo("Mod Info", "No mods with 'required' or 'optional' server_side were found.")
    else:
        messagebox.showinfo("No Mods Found", "No mod IDs were found in the mods folder.")




# search modrinth
def search_mod(mod_id):
    url = f"https://api.modrinth.com/v2/search?query={mod_id}"
    headers = {
        "User-Agent": "Flxrd/ModrinthProfileToServer (flaminxred@gmail.com)"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            if hits:
                top_hit = hits[0]
                title = top_hit.get("title", "Unknown")
                server_side = top_hit.get("server_side", "unknown")
                if server_side in ["required", "optional"]:
                    print(f"Hit: {title} - {server_side}")
                    return {"title": title, "server_side": server_side}
    except Exception as e:
        print(f"Error seaching mod {mod_id}: {e}")
    return None



# Handle profile selection
def select_profile(profile_name, profile_path):
    global selected_profile
    selected_profile = {"name": profile_name, "path": profile_path}
    messagebox.showinfo("Profile Selected", f"Selected: {profile_name}")
    process_mods_in_profile(selected_profile)

# Final step, it's been 15 hours thank fuck
def copy_mod_files(profile, mod_info_list):
    export_dir = os.path.join(os.getcwd(), "exports", profile["name"])
    os.makedirs(export_dir, exist_ok=True)
    
    profile_folder = os.path.join(DEFAULT_PATH, "profiles", profile["path"])
    mods_folder = os.path.join(profile_folder, "mods")

    for info in mod_info_list:
        source_file = os.path.join(mods_folder, info["file"])
        if os.path.exists(source_file):
            shutil.copy2(source_file, export_dir)
            print(f"Copied {info['file']}")
        else:
            print(f"File not found: {source_file}")
    messagebox.showinfo("Copy Complete", f"Copied {len(mod_info_list)} mod file(s) to {export_dir}")



# GUI Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Modrinth Profile Manager")
root.geometry("800x400")

frame = ctk.CTkFrame(root)
frame.pack(pady=20, padx=20, fill='both', expand=True)
label = ctk.CTkLabel(frame, text="Checking for Modrinth Database...", font=("Segoe UI", 14))
label.pack(pady=10)

db_path = check_db()
if db_path:
    label.configure(text=f"Select your profile below")

    # Scrollable container
    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True, padx=20, pady=10)

    canvas = Canvas(container)
    scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Table Header
    headers = ["Profile Name", "Path", "Game Version", "Mod Loader", "Last Modified", "Select"]
    for col, text in enumerate(headers):
        label = ctk.CTkLabel(scrollable_frame, text=text, font=("Segoe UI", 12, "bold"), anchor="w")
        label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

    # Fetch and display profiles
    profiles = get_profiles(db_path)
    if profiles:
        max_display_rows = min(len(profiles), 6)
        row_height = 40
        frame_height = 150 + (max_display_rows * row_height)
        root.geometry(f"800x{frame_height}")

        for row_idx, (path, name, game_version, mod_loader, modified) in enumerate(profiles, start=1):
            modified_text = format_relative_time(modified)
            data = [name, path, game_version, mod_loader, modified_text]

            for col_idx, value in enumerate(data):
                label = ctk.CTkLabel(scrollable_frame, text=str(value), font=("Segoe UI", 11), anchor="w")
                label.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")

            # Select Button
            select_button = ctk.CTkButton(scrollable_frame, text="Create server-side mod list", command=lambda n=name, p=path: select_profile(n, p))
            select_button.grid(row=row_idx, column=len(data), padx=10, pady=5)

    else:
        label.configure(text="No profiles found.")
else:
    label.configure(text="No database selected.")

root.mainloop()
