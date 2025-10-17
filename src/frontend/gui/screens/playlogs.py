from frontend.gui.elements import BasicScreen

__all__ = ["PlayLogs"]

class PlayLogs(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "Play Logs",
            id = "PlayLogsScreen",
            *args, **kwargs
        )