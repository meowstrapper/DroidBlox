from dataclasses import dataclass
from typing import Optional, Union

__all__ = ["LogEntries", "BSRPCAsset", "BSRPCSetRPCData", "BSRPCMessage"]
class LogEntries:
    GameMessageEntry                = "[FLog::Output] [BloxstrapRPC]"
    GameJoiningEntry                = "[FLog::Output] ! Joining game"
    GameTeleportingEntry            = "[FLog::GameJoinUtil] GameJoinUtil::initiateTeleportToPlace"
    GameJoiningPrivateServerEntry   = "[FLog::GameJoinUtil] GameJoinUtil::joinGamePostPrivateServer"
    GameJoiningReservedServerEntry  = "[FLog::GameJoinUtil] GameJoinUtil::initiateTeleportToReservedServer"
    GameJoiningUniverseEntry        = "[FLog::GameJoinLoadTime] Report game_join_loadtime:"
    GameJoiningUDMUXEntry           = "[FLog::Network] UDMUX Address = "
    GameJoinedEntry                 = "[FLog::Network] serverId:"
    GameDisconnectedEntry           = "[FLog::Network] Time to disconnect replication data:"
    GameLeavingEntry                = "[FLog::SingleSurfaceApp] leaveUGCGameInternal"
    RobloxExitedEntry               = "[FLog::SingleSurfaceApp] destroyLuaApp"

    GameJoiningEntryPattern         = r"! Joining game '([0-9a-f\-]{36})' place ([0-9]+) at ([0-9\.]+)"
    GameJoiningPrivateServerPattern = r"""accessCode"":""([0-9a-f\-]{36})"""
    GameJoiningUniversePattern      = r"userid:([0-9]+), .*universeid:([0-9]+)"
    GameJoiningUDMUXPattern         = r"UDMUX Address = ([0-9\.]+)"
    GameJoinedEntryPattern          = r"serverId: ([0-9\.]+)\|[0-9]+"
    GameMessageEntryPattern         = r"\[BloxstrapRPC\] (.*)"

@dataclass
class BSRPCAsset:
    assetId: int
    hoverText: Optional[str] = None
    clear: Optional[bool] = False
    reset: Optional[bool] = False

    @classmethod
    def deserialize(cls, jsonData: dict):
        return cls(**jsonData)

@dataclass
class BSRPCSetRPCData:
    details: Optional[str]
    state: Optional[str] = None
    timeStart: Optional[int] = None
    timeEnd: Optional[int] = None
    smallImage: Optional[BSRPCAsset] = None
    largeImage: Optional[BSRPCAsset] = None

    @classmethod
    def deserialize(cls, jsonData: dict):
        smallImage = jsonData.get("smallImage")
        largeImage = jsonData.get("largeImage")
        if smallImage: jsonData["smallImage"] = BSRPCAsset.deserialize(smallImage)
        if largeImage: jsonData["largeImage"] = BSRPCAsset.deserialize(largeImage)
        return cls(**jsonData)

@dataclass
class BSRPCMessage:
    command: str
    data: Union[str,BSRPCSetRPCData]

    @classmethod
    def deserialize(cls, jsonData: dict):
        command = jsonData.get("command")
        data = jsonData.get("data")
        if command == "SetRichPresence": jsonData["data"] = BSRPCSetRPCData.deserialize(data)
        return cls(**jsonData)