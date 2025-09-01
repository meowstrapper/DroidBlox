from kivy.logger import Logger

from backend.files import paths
from .models import PlaySession

import json
import os
from typing import List

__all__ = ["getPlayLogs", "logPlaySession"]

TAG = "DBPlayLogs" + ": "

Logger.debug(TAG + f"Play logs path is at {paths.dbPlayLogs}")

def getPlayLogs() -> List[PlaySession]:
    Logger.debug(TAG + f"Reading play logs")
    with open(paths.dbPlayLogs, "r") as readPlayLogs:
        return [PlaySession.deserialize(i) for i in json.load(readPlayLogs)]

def logPlaySession(playSession: PlaySession):
    currentPlayLogs = getPlayLogs()
    currentPlayLogs.append(playSession)

    Logger.debug(TAG + f"Writing new play logs: {currentPlayLogs}")
    with open(paths.dbPlayLogs, "w") as writePlayLogs:
        json.dump([i.toDict() for i in currentPlayLogs], writePlayLogs)

def _createPlayLogs():
    with open(paths.dbPlayLogs, "w") as writePlayLogs:
        writePlayLogs.write("[]")

if not os.path.exists(paths.dbPlayLogs):
    Logger.info(TAG + "Play logs doesn't exist, writing it")
    _createPlayLogs()

else:
    try:
        getPlayLogs()
    except Exception as e:
        Logger.error(TAG + f"Failed while trying to get play logs: {e}, overwriting it.")
        _createPlayLogs()
    
