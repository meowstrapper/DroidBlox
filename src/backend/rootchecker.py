# TODO: delete this in the future because of libsu
from kivy.logger import Logger
from typing import Union
import os

TAG = "DBRootChecker" + ": "

__all__ = ["suBinaryPath", "checkForRootAcess"]

def suBinaryToUse() -> Union[bool, str]:
    for i in ["/system/bin/su", "/system/xbin/su", "/system_ext/bin/su", "/sbin/su"]:
        if os.path.exists(i): return i
    return None

suBinaryPath = suBinaryToUse()
Logger.debug(TAG + f"Device is{'' if bool(suBinaryPath) else ' not'} rooted. Using {suBinaryPath}")

def checkForRootAccess():
    if not suBinaryPath:
        return False
        
    try:
        checkRoot = subprocess.check_output([suBinaryPath, "-c", "echo check"])
        if checkRoot.decode().rstrip() == "check":
            return True
    except Exception as e:
        Logger.warn(TAG + f"Error while checking root: {e}")
        return False
