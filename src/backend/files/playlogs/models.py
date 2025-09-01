from dataclasses import dataclass

__all__ = ["PlaySession"]

@dataclass
class PlaySession:
    universeId: int
    playedAt: float
    leftAt: float
    deeplink: str

    @classmethod
    def deserialize(cls, jsonData: dict):
        return cls(**jsonData)
    
    def toDict(self):
        return self.__dict__