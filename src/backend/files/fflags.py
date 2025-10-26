from kivy.logger import Logger
from kivy.utils import platform

from backend.files import paths
from backend.rootchecker import suBinaryPath

import json
import os
import subprocess
from typing import Any, List

TAG = "DBFFlags" + ": "

__all__ = ["readRawFFlags", "readFFlags", "writeToFFlags", "writeFFlag", "mergeFFlags", "deleteFFlags", "applyFFlagsToRoblox"]

Logger.debug(TAG + f"FastFlags are located at {paths.dbFFlags}")

def readRawFFlags() -> str:
    Logger.debug(TAG + "Attempting to read fflags and return as raw")
    with open(paths.dbFFlags, "r") as readFFlag:
        return readFFlag.read()

def readFFlags() -> dict:
    Logger.debug(TAG + "Attempting to read fflags")
    fflags = json.loads(readRawFFlags())
    Logger.debug(TAG + f"Returning fflags: {fflags}")
    return fflags

def writeToFFlags(text: str):
    Logger.debug(TAG + f"Writing to fflags: {text}")
    with open(paths.dbFFlags, "w") as writeFFlag:
        writeFFlag.write(text)

def writeFFlag(fflag: str, value: Any):
    Logger.debug(TAG + f"Attemting to write fflag {fflag} as {value}")
    oldFFlags = readFFlags()
    oldFFlags[fflag] = value
    writeToFFlags(json.dumps(oldFFlags, indent = 4))
    Logger.debug(TAG + f"New fflags: {oldFFlags}")

def mergeFFlags(fflags: dict):
    Logger.debug(TAG + f"Attempting to merge the following fflags: {fflags}")
    oldFFlags = readFFlags()
    oldFFlags.update(fflags)
    writeToFFlags(json.dumps(oldFFlags, indent = 4))
    Logger.debug(TAG + f"New fflags: {oldFFlags}")

def deleteFFlags(fflags: List[str]):
    Logger.debug(TAG + f"Attempting to remove a list of fflags: {fflags}")
    oldFFlags = readFFlags()
    for fflag in fflags:
        try:
            oldFFlags.pop(fflag)
        except:
            Logger.warning(TAG + f"Failed to remove fflag {fflag}, ignoring")
    writeToFFlags(json.dumps(oldFFlags, indent = 4))
    Logger.debug(TAG + f"New fflags: {oldFFlags}")

def applyFFlagsToRoblox():
    Logger.debug(TAG + f"Attempting to apply fflags to roblox")
    subprocess.call([suBinaryPath, "-c", f"mkdir -p {paths._robloxFFlagsFolder} && cp {paths.dbFFlags} {paths.robloxFFlags}"])

try:
    readFFlags()
except:
    Logger.info(TAG + "Creating fflag file")
    with open(paths.dbFFlags, "w") as writeFFlag:
        json.dump({}, writeFFlag)