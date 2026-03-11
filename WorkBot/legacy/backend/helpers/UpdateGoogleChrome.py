import subprocess
import time
import requests
import zipfile
import shutil
from pathlib import Path
import winreg

# Define paths using pathlib
CHROME_PATH        = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CHROME_UPDATE_PATH = Path(r"C:\Program Files\Google\Update\GoogleUpdate.exe")
CHROMEDRIVER_PATH  = Path(r"C:\path\to\chromedriver.exe")
CHROMEDRIVER_DIR   = CHROMEDRIVER_PATH.parent


def get_chrome_version():
    """Retrieve the installed version of Google Chrome from the Windows Registry."""
    print('Searching for Chrome version.')
    try:
        key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            version, _ = winreg.QueryValueEx(key, "version")
            print(f'Chrome version found: {version}', flush=True)
            return version
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
        return None


def update_chrome():
    """Update Google Chrome using winget with elevated privileges."""
    try:
        print("Updating Google Chrome using winget with elevated privileges...")
        subprocess.run([
            "powershell", "Start-Process", "winget", "-ArgumentList", "'upgrade --id=Google.Chrome --silent'", "-Verb", "RunAs"
        ], check=True)
        time.sleep(10)  # Wait for update to finish
        print("Chrome updated successfully!")
    except Exception as e:
        print(f"Error updating Chrome with winget: {e}")



# def get_latest_chromedriver_url(chrome_version):
#     """Find and return the latest ChromeDriver download URL matching the Chrome version."""
#     major_version = chrome_version.split(".")[0]
#     url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         latest_driver_version = response.text.strip()
#         return f"https://chromedriver.storage.googleapis.com/{latest_driver_version}/chromedriver_win32.zip"
#     return None


# def update_chromedriver(chrome_version):
#     """Download and replace ChromeDriver with the correct version."""
#     print("Updating ChromeDriver...")
#     url = get_latest_chromedriver_url(chrome_version)
#     if not url:
#         print("Failed to get ChromeDriver download URL.")
#         return

#     zip_path = CHROMEDRIVER_DIR / "chromedriver.zip"

#     response = requests.get(url, stream=True)
#     if response.status_code == 200:
#         with zip_path.open("wb") as file:
#             file.write(response.content)

#         # Extract and replace existing ChromeDriver
#         with zipfile.ZipFile(zip_path, "r") as zip_ref:
#             zip_ref.extractall(CHROMEDRIVER_DIR)

#         # Cleanup
#         zip_path.unlink()
#         print("ChromeDriver updated successfully!")
#     else:
#         print("Failed to download ChromeDriver.")


def main():
    old_chrome_version = get_chrome_version()
    if not old_chrome_version:
        print("Could not detect Chrome version.")
        return

    update_chrome()

    new_chrome_version = get_chrome_version()

    # # Check if Selenium error is due to version mismatch
    # try:
    #     from selenium import webdriver
    #     from selenium.webdriver.chrome.service import Service
    #     from selenium.webdriver.chrome.options import Options

    #     options = Options()
    #     service = Service(str(CHROMEDRIVER_PATH))
    #     driver = webdriver.Chrome(service=service, options=options)
    #     driver.quit()
    # except Exception as e:
    #     if "only supports Chrome version" in str(e):
    #         print("Chrome version mismatch detected. Updating Chrome and ChromeDriver...")
    #         update_chrome()
    #         time.sleep(10)  # Allow time for update
    #         chrome_version = get_chrome_version()  # Get updated version
    #         # update_chromedriver(chrome_version)
    #     else:
    #         print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
