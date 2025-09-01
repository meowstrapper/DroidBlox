from dataclasses import dataclass
from typing import Any, Dict, List, Optional

__all__ = ["OpCodes", "Payload", "Message",
           "IdentifyPayload", "ResumePayload", "ChangeRPCPayload",
           "RemoveRPCPayload", "Button"]

DROIDBLOX_APPLICATION_ID = 1379313837169311825

class OpCodes:
    DISPATCH = 0 # RECEIVE
    HEARTBEAT = 1 # SEND/RECEIVE
    IDENTIFY = 2 # SEND  
    PRESENCE_UPDATE = 3 # SEND
    RESUME = 6 # SEND
    RECONNECT = 7 # RECEIVE
    INVALID_SESSION = 9 # RECEIVE
    HELLO = 10 # RECEIVE
    HEARTBEAT_ACK = 11 # RECEIVE


@dataclass
class Payload:
    op: int
    data: Optional[Dict[str, Any]]

    def toDict(self) -> dict:
        return {
            "op": self.op,
            "d": self.data
        }
    
@dataclass
class Message(Payload):
    sequence: Optional[int] = None
    event: Optional[str] = None 

    @classmethod
    def deserialize(cls, jsonData: dict):
        return cls(
            op = jsonData.get("op"),
            data = jsonData.get("d"),
            sequence = jsonData.get("s"),
            event = jsonData.get("t")
        )

@dataclass
class IdentifyPayload:
    token: str

    def toDict(self) -> dict:
        return {
            "token": self.token,
            "capabilities": 65,
            "compress": False,
            "largeThreshold": 100, 
            "properties": {
                "os": "Windows",
                "browser": "Discord Client",
                "device": "ktor"
            }
        }

@dataclass
class ResumePayload:
    token: str
    sessionId: str
    lastSeqCode: int

    def toDict(self) -> dict:
        return {
            "token": self.token,
            "session_id": self.sessionId,
            "seq": self.lastSeqCode
        }

@dataclass
class Button:
    label: str
    url: str

@dataclass
class ChangeRPCPayload:
    name: str
    state: Optional[str] = None
    details: Optional[str] = None
    timeStart: Optional[int] = None
    timeEnd: Optional[int] = None
    largeImage: Optional[str] = None
    largeText: Optional[str] = None
    smallImage: Optional[str] = None
    smallText: Optional[str] = None
    buttons: Optional[List[Button]] = None

    def toDict(self) -> dict:
        return {
            "since": 0,
            "afk": False,
            "status": "online",
            "activities": [{
                "name": self.name,
                "state": self.state,
                "details": self.details,
                "party": None,
                "type": 0, # PLAYING
                "timestamps": {
                    "start": self.timeStart,
                    "end": self.timeEnd
                },
                "assets": {
                    "large_image": self.largeImage,
                    "large_text": self.largeText,
                    "small_image": self.smallImage,
                    "small_text": self.smallText,
                },
                "buttons": [i.label for i in self.buttons] if self.buttons else None,
                "metadata": {"button_urls": [i.url for i in self.buttons]} if self.buttons else None,
                "application_id": DROIDBLOX_APPLICATION_ID,
                "url": None
            }]
        }

@dataclass
class RemoveRPCPayload:
    def toDict(self) -> dict:
        return {
            "since": 0,
            "afk": False,
            "status": "online",
            "activities": []
        }