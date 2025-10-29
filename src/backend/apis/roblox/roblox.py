from kivy.logger import Logger
from typing import List
import requests

from .models import *

__all__ = ["getGameInfo", "getThumbnails", "getUserInfo"]

TAG = "DBRobloxAPI" + ": "

def getGameInfo(universeIds: List[int]) -> List[Game]:
    requestTo = f"https://games.roblox.com/v1/games?universeIds={','.join([str(i) for i in universeIds])}"

    Logger.debug(TAG + f"Requesting GET to {requestTo}")
    gameInfosReq = requests.get(requestTo)
    if gameInfosReq.status_code != 200:
        Logger.error(TAG + f"Failed to get roblox game info. Got {gameInfosReq.status_code}\nText:\n{gameInfosReq.text}")
        return
    
    return [
        game
        for universeId in universeIds
        for game in [Game.deserialize(gameInfo) for gameInfo in gameInfosReq.json()["data"]]
        if game.universeId == universeId
    ] # roblox fucks up the returned data if there are duplicates of universe ids

def getUserInfo(userId: int) -> User:
    requestTo = f"https://users.roblox.com/v1/users/{userId}"

    Logger.debug(TAG + f"Requesting GET to {requestTo}")
    usernameReq = requests.get(requestTo)
    if usernameReq.status_code != 200:
        Logger.error(TAG + f"Failed to get roblox user info. Got {usernameReq.status_code}\nText:\n{usernameReq.text}")
        return

    return User.deserialize(usernameReq.json())

def getThumbnails(thumbnails: List[Thumbnail]) -> List[str]:
    requestTo = f"https://thumbnails.roblox.com/v1/batch"
    jsonToSend = [thumbnail.toDict() for thumbnail in thumbnails]

    Logger.debug(TAG + f"Requesting POST to {requestTo} with json {jsonToSend}")
    thumbnailsReq = requests.post(requestTo, json = jsonToSend)
    if thumbnailsReq.status_code != 200:
        Logger.error(TAG + f"Failed to get roblox thumbnail(s). Got {thumbnailsReq.status_code}\nText:\n{thumbnailsReq.text}")
        return
    
    return [thumbnail["imageUrl"] for thumbnail in thumbnailsReq.json()["data"]]
