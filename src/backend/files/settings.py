from kivy.logger import Logger

from backend.files import paths

import json
import os
from typing import Any

TAG = "DBSettings" + ": "

__all__ = ["readSettings", "writeSetting"]

settingTemplate = {
    "enableActivityTracking": True,
    "showServerLocation": False,
    "token": None,
    "showGameActivity": True,
    "allowActivityJoining": False,
    "showRobloxUser": False,
    "applyFFlags": True
}

Logger.debug(TAG + f"Settings are located at {paths.dbSettings}")

def readSettings() -> dict:
    Logger.debug(TAG + "Attempting to read settings")
    with open(paths.dbSettings, "r") as readSettings:
        settings = json.load(readSettings)
        toLog = settings.copy()
        toLog["token"] = "[REDACTED]"
        Logger.debug(TAG + f"Returning settings: {toLog}")
        return settings

def writeSetting(setting: str, value: Any):
    Logger.debug(TAG + f"Attemting to write setting {setting}" + (f"as {value}" if setting != "token" else ''))
    oldSettings = readSettings()
    oldSettings[setting] = value
    toLog = oldSettings.copy()
    toLog["token"] = "[REDACTED]"
    with open(paths.dbSettings, "w") as writeSettings:
        json.dump(oldSettings, writeSettings)
        Logger.debug(TAG + f"New settings: {toLog}")
        


try:
    readSettings()
except:
    Logger.info(TAG + "Creating settings file")
    with open(paths.dbSettings, "w") as writeSettings:
        json.dump(settingTemplate, writeSettings)