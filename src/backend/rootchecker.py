from kivy.logger import Logger
from typing import Union
import os

TAG = "DBRootChecker" + ": "

__all__ = ["suBinaryPath"]

def suBinaryToUse() -> Union[bool, str]:
    for i in ["/system/bin/su", "/system/xbin/su", "/system_ext/bin/su", "/sbin/su"]:
        if os.path.exists(i): return i
    return None
suBinaryPath = suBinaryToUse()
Logger.debug(TAG + f"Device is{'' if bool(suBinaryPath) else ' not'} rooted. Using {suBinaryPath}")