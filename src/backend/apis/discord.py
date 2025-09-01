from kivy.logger import Logger
from typing import List
import requests

__all__ = ["getMPOfUrls", "getUsername"]

TAG = "DBDiscordAPI" + ": "

DROIDBLOX_APPLICATION_ID = 1379313837169311825

def getMPOfUrls(token: str, urls: List[str]) -> List[str]:
    requestTo = f"https://discord.com/api/v9/applications/{DROIDBLOX_APPLICATION_ID}/external-assets"
    jsonToSend = {"urls": urls}
    headers = {"Authorization": token}

    Logger.debug(TAG + f"Requesting POST to {requestTo} with json {jsonToSend}")
    mediaProxyReq = requests.post(requestTo, json = jsonToSend, headers = headers)
    if mediaProxyReq.status_code != 200:
        Logger.error(TAG + f"Failed to get media proxy of urls. Got {mediaProxyReq.status_code}\nText:\n{mediaProxyReq.text}")
        return
    
    return [f"mp:{i['external_asset_path']}" for i in mediaProxyReq.json()]

def getUsername(token: str) -> str:
    requestTo = f"https://discord.com/api/v9/users/@me"
    headers = {"Authorization": token}

    Logger.debug(TAG + f"Requesting GET to {requestTo}")
    usernameReq = requests.get(requestTo, headers = headers)
    if usernameReq.status_code != 200:
        Logger.error(TAG + f"Failed to get the discord username. Got {usernameReq.status_code}\nText:\n{usernameReq.text}")
        return
    
    return usernameReq.json()["username"]

def logout(token: str):
    # basically make the token useless
    requestTo = "https://discord.com/api/v9/auth/logout"
    jsonToSend = {"provider": None, "voip_provider": None}
    headers = {"Authorization": token}

    Logger.debug(TAG + f"Requesting POST to {requestTo}")
    logoutReq = requests.post(requestTo, json = jsonToSend, headers = headers)
    if logoutReq.status_code != 204 or logoutReq.status_code != 200:
        Logger.error(TAG + f"Failed to logout discord token. Got {logoutReq.status_code}\nText:\n{logoutReq.text}")
