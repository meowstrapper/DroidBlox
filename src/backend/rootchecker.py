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

def checkForRootAccess():
    if not suBinaryToUse():
        return False
        
    try:
        checkRoot = subprocess.check_output([suBinaryToUse(), "-c", "echo check"])
        if checkRoot.decode().rstrip() == "check":
            return True
    except:
        return False

suBinaryPath = suBinaryToUse()
Logger.debug(TAG + f"Device is{'' if bool(suBinaryPath) else ' not'} rooted. Using {suBinaryPath}")