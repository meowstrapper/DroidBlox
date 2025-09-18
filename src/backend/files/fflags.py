from kivy.logger import Logger
from kivy.utils import platform

from backend.files import paths
from backend.rootchecker import suBinaryPath

import json
import os
import subprocess
from typing import Any, List

TAG = "DBFFlags" + ": "

__all__ = ["readFFlags", "writeFFlag", "mergeFFlags", "deleteFFlags", "applyFFlagsToRoblox"]

Logger.debug(TAG + f"FastFlags are located at {paths.dbFFlags}")

if platform == "android":
    from jnius import autoclass
    ExtendedFile = autoclass("com.topjohnwu.superuser.nio.ExtendedFile")
else:
    Logger.debug(TAG + f"Running on {platform}, not importing")

def readFFlags() -> dict:
    Logger.debug(TAG + "Attempting to read fflags")
    with open(paths.dbFFlags, "r") as readFFlag:
        fflags = json.load(readFFlag)
        Logger.debug(TAG + f"Returning fflags: {fflags}")
        return fflags

def writeFFlag(fflag: str, value: Any):
    Logger.debug(TAG + f"Attemting to write fflag {fflag} as {value}")
    oldFFlags = readFFlags()
    oldFFlags[fflag] = value
    with open(paths.dbFFlags, "w") as writeFFlag:
        json.dump(oldFFlags, writeFFlag)
        Logger.debug(TAG + f"New fflags: {oldFFlags}")

def mergeFFlags(fflags: dict):
    Logger.debug(TAG + f"Attempting to merge the following fflags: {fflags}")
    oldFFlags = readFFlags()
    oldFFlags.update(fflags)
    with open(paths.dbFFlags, "w") as writeFFlag:
        json.dump(oldFFlags, writeFFlag)
        Logger.debug(TAG + f"New fflags: {oldFFlags}")

def deleteFFlags(fflags: List[str]):
    Logger.debug(TAG + f"Attempting to remove a list of fflags: {fflags}")
    oldFFlags = readFFlags()
    for fflag in fflags:
        try:
            oldFFlags.pop(fflag)
        except:
            Logger.warning(TAG + f"Failed to remove fflag {fflag}, ignoring")
    with open(paths.dbFFlags, "w") as writeFFlag:
        json.dump(oldFFlags, writeFFlag)
        Logger.debug(TAG + f"New fflags: {oldFFlags}")

def applyFFlagsToRoblox():
    Logger.debug(TAG + f"Attempting to apply fflags to roblox")
    # subprocess.call([suBinaryPath, "-c", f"mkdir -p {paths._robloxFFlagsFolder}"])
    # subprocess.call([suBinaryPath, "-c", f"cp {paths.dbFFlags} {paths.robloxFFlags}"])
    
    try:
        robloxFFlags = ExtendedFile(paths.robloxFFlags)
        robloxFFlagsFolder = robloxFFlags.getParentFile()
        if not robloxFFlagsFolder.exists():
            Logger.debug(TAG + "Creating ClientSettings folder")
            robloxFFlagsFolder.mkdir()
        Logger.debug(TAG + "Writing to ClientAppSettings.json")
        robloxFFlags

    except Exception as e:
        Logger.error(TAG + f"Something went wrong while trying to apply fflags! Error: {e}")
try:
    readFFlags()
except:
    Logger.info(TAG + "Creating fflag file")
    with open(paths.dbFFlags, "w") as writeFFlag:
        json.dump({}, writeFFlag)