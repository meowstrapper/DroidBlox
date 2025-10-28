# TODO: find a way to only show one toast when using su
from kivy.logger import Logger

from backend.apis import discord, roblox
from backend.files import settings, playlogs
from backend.rootchecker import suBinaryPath
from backend.threadtools import scheduleInClock

import backend.rpc as rpc
from .models import *

from dataclasses import replace as cloneDataclass
import json
import re
import subprocess
import threading
import time
import urllib

from android_notify import Notification
import requests

TAG = "DBActivityWatcher" + ": "

__all__ = ["fetchIPLocation", "ActivityWatcherSession"]
cachedRoSealListOfIP = {}

def getIPLocationWithIPInfo(ip: str):
    requestTo = f"https://ipinfo.io/{ip}/json"
    Logger.debug(TAG + f"Requesting GET to {requestTo}")
    ipInfoReq = requests.get(requestTo)
    if ipInfoReq.status_code != 200:
        Logger.error(TAG + f"Failed to get the ip location with IPInfo.io. Got {ipInfoReq.status_code}\nText:\n{ipInfoReq.text}")
        return
    location = ipInfoReq.json()
    if location["city"] == location["region"]:
        return f"{location['region']}, {location['country']}"
    else:
        return f"{location['city']}, {location['region']}, {location['country']}"

def getIPLocationWithRoSeal(ip: str):
    global cachedRoSealListOfIP
    if not cachedRoSealListOfIP:
        requestTo = f"https://raw.githubusercontent.com/RoSeal-Extension/Top-Secret-Thing/refs/heads/main/data/datacenters.json"
        Logger.debug(TAG + f"Requesting GET to {requestTo}")
        rosealReq = requests.get(requestTo)
        if rosealReq.status_code != 200:
            Logger.error(TAG + f"Failed to get the list of ip locations. Got {rosealReq.status_code}\nText:\n{rosealReq.text}")
            return
        cachedRoSealListOfIP = rosealReq.json()
    
    for location in cachedRoSealListOfIP:
        if ip in location["ips"]:
            location = location["location"]
            if location["city"] == location["region"]:
                return f"{location['city']}, {location['country']}"
            else:
                return f"{location['city']}, {location['region']}, {location['country']}"
    return None

def fetchIPLocation(ip: str):
    Logger.debug(TAG + "Attempting to get IP Location with RoSeal's list of ips")
    try:
        location = getIPLocationWithRoSeal(ip)
        if not location:
            raise Exception("Didn't find the IP Location")
        else:
            Logger.debug(TAG + f"IP Location: {location}")
        return location
    except Exception as e:
        Logger.error(TAG + f"Something went wrong!: {e}, falling back to IpInfo.io")
        location = getIPLocationWithIPInfo(ip)
        if not location:
            Logger.error(TAG + "Couldn't find the IP Location too, returning none!")
            return "N/A, N/A, N/A"
        else:
            Logger.debug(TAG + f"IP Location: {location}")
        return location

def getRobloxPID() -> int:
    return int(subprocess.check_output([suBinaryPath, "-c", "pidof com.roblox.client"]).decode(errors = "ignore"))

class ActivityWatcherSession:
    def __init__(self):

        self.process: subprocess.Popen = None
        self.lastTimeOfLogEntry: float = None
        self.stopMonitoringEvent = threading.Event()
        
        self.rpcSession: rpc.RPCSession = None
        self.originalRPCArgs: rpc.models.ChangeRPCPayload = None
        self.startedAt: float = None
        self.lastRPCRequestTime: float = None

        self.placeId: int = None
        self.universeId: int = None
        self.jobId: str = None
        self.udmuxIp: str = None
        self.userId: int = None
        self.playedAt: float = None
        self.leftAt: float = None

    @scheduleInClock
    def _checkIfRobloxExited(self):
        shellScript = "while true; do if [[ -z $(pidof com.roblox.client) ]]; then exit 1; fi; sleep 1; done"
        try:
            subprocess.call([suBinaryPath, "-c", shellScript])
        except:
            Logger.info(TAG + "Roblox exited!")
            if self.placeId:
                Logger.info(TAG + "Attempting to log play session before killing the activity watcher:3")
                self._logPlaySession()
            Logger.info(TAG + "Killing activity watcher")
            self.stop()


    @scheduleInClock
    def _startMonitoring(self):
        Logger.debug(TAG + f"Attempting to get Roblox PID (delay per 2 sec)")
        while True:
            try:
                robloxPID = getRobloxPID()
                break
            except:
                Logger.debug(TAG + f"Failed to get Roblox PID, delaying")
        
        Logger.debug(TAG + f"Attempting to logcat roblox (pid is {robloxPID})")
        self.process = subprocess.Popen(
            [suBinaryPath, "-c", f"logcat --pid {str(robloxPID)}"],
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )

        Logger.debug(TAG + "Starting to monitor whether roblox exited")
        self._checkIfRobloxExited()

        while (not self.stopMonitoringEvent.is_set()) or (self.process.poll() is None):
            logEntry: str = self.process.stdout.readline().decode(errors = "ignore")
            self.lastTimeOfLogEntry = time.time()

            try:
                if LogEntries.GameJoiningEntry in logEntry:
                    self.playedAt = time.time()

                    matchedRegex = re.search(LogEntries.GameJoiningEntryPattern, logEntry)
                    self.placeId = int(matchedRegex.group(2))
                    self.jobId = matchedRegex.group(1)
                    Logger.info(TAG + f"Joining place id {self.placeId} at {self.jobId}")

                elif LogEntries.GameJoiningUniverseEntry in logEntry:
                    matchedRegex = re.search(LogEntries.GameJoiningUniversePattern, logEntry)
                    self.userId = int(matchedRegex.group(1))
                    self.universeId = int(matchedRegex.group(2))
                    Logger.info(TAG + f"Joining as {self.userId} in universe id {self.universeId}")
                    
                elif LogEntries.GameJoiningUDMUXEntry in logEntry:
                    matchedRegex = re.search(LogEntries.GameJoiningUDMUXPattern, logEntry)
                    self.udmuxIp = matchedRegex.group(1)
                    Logger.info(TAG + f"UDMUX IP: {self.udmuxIp}")

                elif LogEntries.GameJoinedEntry in logEntry:
                    Logger.info(TAG + "Joined the server! (Setting RPC and notifications if user agreed)")
                    if self.rpcSession: 
                        Logger.debug
                        self._handleServerJoined(time.time())
                    if settings.readSettings()["showServerLocation"]:
                        self._handleNotifyServerLocation()

                elif LogEntries.GameMessageEntry in logEntry:
                    matchedRegex = re.search(LogEntries.GameMessageEntryPattern, logEntry)
                    deserializeToJson = json.loads(matchedRegex.group(1))
                    deserializeToMessage = BSRPCMessage.deserialize(deserializeToJson)

                    Logger.info(TAG + f"Received BloxstrapRPC Message: {deserializeToMessage}")

                    if self.rpcSession:
                        if self.lastRPCRequestTime and (time.time() - self.lastRPCRequestTime) >= 1:
                            Logger.info(TAG + f"Dropping RPC Message as rate limit has been hit")
                        self.lastRPCRequestTime = time.time()
                        self._handleBloxstrapRPC(deserializeToMessage)
                    
                    else:
                        Logger.debug(TAG + "Ignoring BloxstrapRPC message, rpc disabled")
                elif LogEntries.GameDisconnectedEntry in logEntry:
                    Logger.info(TAG + "Leaving the game, logging play logs, resetting everything (and setting back RPC)")
                    self._logPlaySession()
                    self.placeId = None
                    self.universeId = None
                    self.jobId = None
                    self.udmuxIp = None
                    self.userId = None
                    self.playedAt = None
                    self.leftAt = time.time()
                    if self.rpcSession:
                        self.rpcSession.changeRPC(rpc.models.ChangeRPCPayload(
                            name = "Roblox",
                            timeStart = int(self.startedAt) * 1000
                        ))

            except Exception as e:
                Logger.error(TAG + f"Something went wrong!; {e}\nLog Entry: {logEntry}")
        
        Logger.info(TAG + f"Activity watcher ended! Resetting everything")
        self.placeId = None
        self.universeId = None
        self.jobId = None
        self.udmuxIp = None
        self.userId = None

    def start(self):
        self.startedAt = time.time()
        self.currentSettings = settings.readSettings()

        Logger.info(TAG + f"Initializing activity watcher")
        self._startMonitoring()
        if self.currentSettings["token"] and self.currentSettings["showGameActivity"]:
            Logger.info(TAG + f"Initializing rpc session")
            self.rpcSession = rpc.RPCSession()
            self.rpcSession.changeRPC(rpc.models.ChangeRPCPayload(
                name = "Roblox",
                timeStart = int(self.startedAt) * 1000
            ))
            self.rpcSession.start()
    
    def stop(self):
        self.process.terminate()
        if self.rpcSession:
            self.rpcSession.stop()
        
    @scheduleInClock
    def _handleNotifyServerLocation(self):
        location = fetchIPLocation(self.udmuxIp)
        if not location:
            return
        Logger.info(TAG + f"Connected at {location}")
        notification = Notification(
            title = "Connected to server",
            message = f"Located at {location}"
        )
        notification.addLine(f"Place ID: {self.placeId}")
        notification.addLine(f"Job ID: {self.jobId}")
        notification.addLine(f"UDMUX IP: {self.udmuxIp}")

        Logger.debug(TAG + f"Sending out notification")
        notification.send()
    
    @scheduleInClock
    def _handleServerJoined(self):
        Logger.debug(TAG + f"Fetching game (and user) thumbnail url")
        thumbnailUrls = roblox.getThumbnails([
            roblox.models.Thumbnail(
                targetId = self.universeId,
                type = "GameIcon",
                size = "512x512",
                isCircular = False
            )
        ] + ([
            roblox.models.Thumbnail(
                targetId = self.userId,
                type = "AvatarHeadShot",
                size = "75x75",
                isCircular = True
            )
        ] if self.currentSettings["showRobloxUser"] else []))
        if not thumbnailUrls:
            Logger.error(TAG + f"Something went wrong with Roblox's Thumbnail API! Doing nothing.")
            return
        
        Logger.debug(TAG + f"Returned URLs: {thumbnailUrls}")

        Logger.debug(TAG + "Getting media proxies of the thumbnail urls")
        mpUrls = discord.getMPOfUrls(self.rpcSession.token, thumbnailUrls)
        if not mpUrls:
            Logger.error(TAG + f"Something went wrong with Discord's Media Proxy API! Doing nothing.")
            return
        
        Logger.debug(TAG + f"Getting name of game")
        gameInfo = roblox.getGameInfo([self.universeId])
        if not gameInfo:
            Logger.error(TAG + f"Something went wrong with Roblox's Game API! Doing nothing.")
            return
        gameName = gameInfo[0].name
        gameCreator = gameInfo[0].creator
        Logger.debug(TAG + f"{gameName} by {gameCreator}")

        if self.currentSettings["showRobloxUser"]:
            userInfo = roblox.getUserInfo(self.userId)
        
        Logger.debug(TAG + "Setting RPC")
        rpcToSet = rpc.models.ChangeRPCPayload(
            name = "Roblox",
            details = gameName,
            state = f"by {gameCreator}",
            timeStart = int(self.playedAt) * 1000,
            largeImage = mpUrls[0],
            largeText = gameName,
            smallImage = mpUrls[1] if self.currentSettings["showRobloxUser"] else None,
            smallText = f"Playing on {userInfo.name} (@{userInfo.displayName})" if self.currentSettings["showRobloxUser"] else None,
            buttons = [rpc.models.Button(
                label = "See game page",
                url = f"https://roblox.com/games/{self.placeId}"
            )] + ([rpc.models.Button(
                label = "Join server",
                url = f"https://roblox.com/games/start?placeId={self.placeId}&gameInstanceId={self.jobId}"
            )] if self.currentSettings["allowActivityJoining"] else [])
        )
        Logger.debug(TAG + f"Setting RPC Arguments: {rpcToSet}")
        self.originalRPCArgs = rpcToSet
        self.rpcSession.changeRPC(rpcToSet)
    
    @scheduleInClock
    def _handleBloxstrapRPC(self, message: BSRPCMessage):
        if message.command == "SetLaunchData" and self.currentSettings["allowActivityJoining"]:
            rpcToSet = cloneDataclass(self.originalRPCArgs)
            rpcToSet.buttons[0].url += "&launchData" + urllib.parse.quote(message.data)

            Logger.debug(TAG + f"Changing RPC")
            self.rpcSession.changeRPC(rpcToSet)
        else:
            dataRequest: BSRPCSetRPCData = message.data
            rpcToSet = cloneDataclass(self.originalRPCArgs)

            if dataRequest.details:
                if len(dataRequest.details) > 128:
                    Logger.error(TAG + f"Details requested is 128 chars longer!")
                elif dataRequest.details == "<reset>":
                    rpcToSet.details = self.originalRPCArgs.details
                else:
                    rpcToSet.details = dataRequest.details
            if dataRequest.state:
                if len(dataRequest.state) > 128:
                    Logger.error(TAG + f"State requested is 128 chars longer!")
                elif dataRequest.state == "<reset>":
                    rpcToSet.state = self.originalRPCArgs.state
                else:
                    rpcToSet.state = dataRequest.state
            
            if dataRequest.timeStart:
                if type(dataRequest.timeStart) == int:
                    rpcToSet.timeStart = dataRequest.timeStart * 1000
                else:
                    rpcToSet.timeStart = None
            if dataRequest.timeEnd:
                if type(dataRequest.timeEnd) == int:
                    rpcToSet.timeEnd = dataRequest.timeEnd * 1000
                else:
                    rpcToSet.timeEnd = None
            
            if dataRequest.largeImage:
                if dataRequest.largeImage.clear:
                    rpcToSet.largeImage = None
                    rpcToSet.largeText = None
                elif dataRequest.largeImage.reset:
                    rpcToSet.largeImage = self.originalRPCArgs.largeImage
                    rpcToSet.largeText = self.originalRPCArgs.largeText
                else:
                    rpcToSet.largeText = dataRequest.largeImage.hoverText
            if dataRequest.smallImage:
                if dataRequest.smallImage.clear:
                    rpcToSet.smallImage = None
                    rpcToSet.smallText = None
                elif dataRequest.smallImage.reset:
                    rpcToSet.smallImage = self.originalRPCArgs.smallImage
                    rpcToSet.smallText = self.originalRPCArgs.smallText
                else:
                    rpcToSet.smallText = dataRequest.smallImage.hoverText
            if dataRequest.smallImage or dataRequest.largeImage:
                Logger.debug(TAG + "Requesting thumbnail url for image id")
                thumbnailUrls = roblox.getThumbnails(([roblox.models.Thumbnail(
                    targetId = dataRequest.largeImage.assetId,
                    type = "Asset",
                    size = "512x512",
                    isCircular = False
                )] if dataRequest.largeImage else []) + ([roblox.models.Thumbnail(
                    targetId = dataRequest.smallImage.assetId,
                    type = "Asset",
                    size = "75x75",
                    isCircular = False
                )] if dataRequest.smallImage else []))
                if not thumbnailUrls:
                    Logger.error(TAG + f"Something went wrong with Roblox's Thumbnail API! Doing nothing.")
                    return

                Logger.debug(TAG + f"Requesting media proxies of image ids")
                mpUrls = discord.getMPOfUrls(self.rpcSession.token, thumbnailUrls)
                if not mpUrls:
                    Logger.error(TAG + f"Something went wrong with Discord's Media Proxy API! Doing nothing.")
                    return
                
                if len(mpUrls) == 2:
                    rpcToSet.largeImage = mpUrls[0]
                    rpcToSet.smallImage = mpUrls[1]
                elif dataRequest.largeImage:
                    rpcToSet.largeImage = mpUrls[0]
                elif dataRequest.smallImage:
                    rpcToSet.smallImage = mpUrls[0]
            
            Logger.debug(TAG + f"Changing RPC")
            self.rpcSession.changeRPC(rpcToSet)

    def _logPlaySession(self):
        Logger.debug(TAG + f"Logging play session after playing")
        playlogs.logPlaySession(playlogs.models.PlaySession(
            universeId = self.universeId,
            playedAt = self.playedAt,
            leftAt = self.leftAt,
            deeplink = f"https://roblox.com/games/start?placeId={self.placeId}&gameInstanceId={self.jobId}"
        ))