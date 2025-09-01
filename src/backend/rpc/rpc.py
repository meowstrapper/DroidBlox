from kivy.logger import Logger
from websockets.sync.client import connect
import websockets

import certifi
import json
import logging
import ssl
import threading
import time

from backend.files import settings
from .models import *

__all__ = ["RPCSession"]

TAG = "DBDiscordRPC" + ": "

pathToCertifi = certifi.where()
sslContext = ssl.create_default_context(cafile = pathToCertifi)
Logger.debug(TAG + f"Using certifi file {pathToCertifi}")

logging.getLogger("websockets").setLevel(logging.INFO)

class RPCSession:
    def __init__(self):
        self.token = settings.readSettings()["token"]

        self.url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.ws: websockets.ClientConnection

        self._heartbeatInterval: float = None
        self._heartbeatStop = threading.Event()

        self._sentHeartbeatAt: float = None
        self.gatewayLatency: float = None

        self.ready = False
        self.sessionId: str = None
        self.lastSeqCode: int = 0

        self.lastRPC: ChangeRPCPayload = None
    
    def start(self):
        threading.Thread(target = self._start).start()
        
    def _start(self):
        Logger.debug(TAG + f"Connecting to {self.url}")
        try:
            with connect(self.url, max_size = None, ssl = sslContext) as ws:
                self.ws = ws

                Logger.debug(TAG + "Starting message processor")
                self.processMessages()

        except websockets.ConnectionClosed as e:
            Logger.info(TAG + f"Connection closed! Code: {e.code} Reason: {e.reason}")
            if e.code == 4000:
                Logger.info(TAG + "Attempting to reconnect")
                self.reconnect()
    
    def stop(self):
        Logger.debug(TAG + "Stopping RPC")
        self._heartbeatStop.set()
        try:
            self.ws.close()
        except: ...
    
    def reconnect(self):
        Logger.debug(TAG + "Reconnecting RPC")
        self.stop()
        self.start()

    def processMessages(self):
        for rawMessage in self.ws:
            message = Message.deserialize(json.loads(rawMessage))
            Logger.debug(TAG + f"Received op code {message.op} event {message.event} sequence {message.sequence}")

            if message.op == OpCodes.HELLO:
                self._heartbeatInterval = message.data.get("heartbeat_interval") / 1000
                Logger.info(TAG + f"Received hello, heartbeat interval is {self._heartbeatInterval}s")

                Logger.debug(TAG + f"Starting heartbeat loop")
                self.startHeartbeatLoop()

                if self.sessionId:
                    Logger.info(TAG + "Attempting to resume")
                    self.sendResume()
                else:
                    Logger.info(TAG + "Identifying")
                    self.sendIdentify()

            elif message.op == OpCodes.DISPATCH:
                if message.event == "READY":
                    self.sessionId = message.data.get("session_id")
                    self.url = message.data.get("resume_gateway_url") + "/?v=10&encoding=json"
                    Logger.debug(TAG + f"Ready! Session ID is {self.sessionId} and new url is {self.url}")
                    self.ready = True
                    self.onReady()
                    
                elif message.event == "RESUMED":
                    Logger.debug(TAG + "Resumed successfully!")
                    self.ready = True
                
                if (message.event == "READY" or message.event == "RESUMED") and self.lastRPC:
                    Logger.debug(TAG + "RPC was set, setting it back")
                    self.changeRPC(self.lastRPC)

            elif message.op == OpCodes.INVALID_SESSION:
                Logger.info(TAG + "Invalid session received, identifying instead.")
                self.sendIdentify()
            
            elif message.op == OpCodes.RECONNECT:
                Logger.info(TAG + "Discord asked us to reconnect, reconnecting!")
                self.reconnect()

            elif message.op == OpCodes.HEARTBEAT_ACK:
                self.gatewayLatency = (time.time() - self._sentHeartbeatAt) * 1000
                Logger.debug(TAG + f"Received heartbeat ack. Gateway latency is {self.gatewayLatency}ms")
                self.gatewayLatencyChanged(self.gatewayLatency)
            
            self.lastSeqCode = message.sequence

    def startHeartbeatLoop(self):
        threading.Thread(target = self._heartbeatLoop).start()

    def _heartbeatLoop(self):
        while not self._heartbeatStop.wait(timeout = self._heartbeatInterval):
            self.sendPayload(Payload(
                op = OpCodes.HEARTBEAT,
                data = {}
            ))
            self._sentHeartbeatAt = time.time()

        Logger.debug(TAG + "Heartbeat loop has been stopped.")
        
    def sendPayload(self, payload: Payload):
        Logger.debug(TAG + f"Sending {payload.data} with op code {payload.op}".replace(self.token, "REDACTED"))
        self.ws.send(json.dumps(payload.toDict()))
    
    def sendIdentify(self):
        self.sendPayload(Payload(
            op = OpCodes.IDENTIFY,
            data = IdentifyPayload(self.token).toDict()
        ))
    
    def sendResume(self):
        self.sendPayload(Payload(
            op = OpCodes.RESUME,
            data = ResumePayload(
                token = self.token,
                sessionId = self.sessionId,
                lastSeqCode = self.lastSeqCode
            ).toDict()
        ))

    def changeRPC(self, rpcArgs: ChangeRPCPayload):
        self.lastRPC = rpcArgs

        if self.ready:
            self.sendPayload(Payload(
                op = OpCodes.PRESENCE_UPDATE,
                data = rpcArgs.toDict()
            ))
        else:
            Logger.debug(TAG + "Not ready yet, letting the message processor change the RPC instead.")
    
    def removeRPC(self):
        self.lastRPC = None
        self.sendPayload(Payload(
            op = OpCodes.PRESENCE_UPDATE,
            data = RemoveRPCPayload().toDict()
        ))
    
    # callbacks
    def onReady(self): ...
    def gatewayLatencyChanged(self, latency: int): ...