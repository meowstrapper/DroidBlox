from kivy.logger import Logger
from kivy.utils import platform

import os

__all__ = ["dbPath", "dbPlayLogs", "dbFFlags", "dbSettings", "robloxPath", "robloxLogs", "_robloxFFlagsFolder", "robloxFFlags"]

TAG = "DBPath" + ": "

if platform == "android":
    Logger.debug(TAG + "Running on android, importing classes")
    from android.storage import app_storage_path # type: ignore
    dbPath = app_storage_path()
else:
    dbPath = os.path.expanduser("~/.droidblox")
    os.makedirs(dbPath, exist_ok = True)

Logger.debug(TAG + f"Default path is {dbPath}")

dbPlayLogs = os.path.join(dbPath, "playlogs.json")
dbFFlags = os.path.join(dbPath, "fflags.json")
dbSettings = os.path.join(dbPath, "settings.json")

robloxPath = "/data/user/0/com.roblox.client/"
robloxLogs = os.path.join(robloxPath, "files", "appData", "logs")
_robloxFFlagsFolder = os.path.join(robloxPath, "files", "exe", "ClientAppSettings")
robloxFFlags = os.path.join(_robloxFFlagsFolder, "ClientAppSettings.json")