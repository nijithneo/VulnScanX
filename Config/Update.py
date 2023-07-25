import os
import requests
import hashlib
import shutil

GITHUB_API_URL = "https://api.github.com/repos/neoxxz/VulnScanX/releases/latest"
MAIN_SCRIPT = "main.py"

def get_local_version():
    try:
        with open(MAIN_SCRIPT, 'r', encoding='utf-8') as f:
            script_content = f.read()
            return hashlib.md5(script_content.encode()).hexdigest()
    except FileNotFoundError:
        print("Local script file not found.")
        return None

def get_remote_version():
    try:
        response = requests.get(GITHUB_API_URL)
        if response.status_code == 200:
            release_data = response.json()
            assets = release_data.get("assets", [])
            for asset in assets:
                if asset.get("name") == MAIN_SCRIPT:
                    return asset.get("browser_download_url")
        print("Failed to fetch remote version.")
        return None
    except requests.exceptions.RequestException:
        print("Failed to fetch remote version.")
        return None

def download_updated_script(url):
    try:
        response = requests.get(url, stream=True)
        with open(MAIN_SCRIPT, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        return True
    except requests.exceptions.RequestException:
        print("Failed to download updated script.")
        return False

def update_main_script():
    local_version = get_local_version()
    remote_url = get_remote_version()

    if local_version and remote_url:
        print("Checking for updates...")
        if local_version != remote_url:
            print("New version is available! Updating...")
            if download_updated_script(remote_url):
                print("Update successful. Please restart the script to use the latest version.")
            else:
                print("Update failed. Please try again later.")
        else:
            print("No updates available.")
    else:
        print("Failed to check for updates.")

if __name__ == "__main__":
    update_main_script()
