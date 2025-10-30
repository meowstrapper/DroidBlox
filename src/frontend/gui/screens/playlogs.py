# TODO: efficient loading

from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.fitimage import FitImage

from backend.apis.roblox import getGameInfo, getThumbnails
from backend.apis.roblox.models import Thumbnail, Game
from backend.files.playlogs import getPlayLogs
from backend.launchRoblox import launchRoblox
from backend.threadtools import scheduleInClock
from frontend.gui.elements import BasicScreen, FixMDLabel

from datetime import datetime
import time

__all__ = ["PlayLogs"]

TAG = "DBPlayLogs" + ": "

class RecentGamePlayed(MDBoxLayout):
    gameName = StringProperty()
    gameCreator = StringProperty()
    gameIconUrl = StringProperty()
    playedAt = NumericProperty() # epoch time
    leftAt = NumericProperty() # epoch time
    robloxDeeplink = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size_hint = (1, None)
        self.height = dp(130)
        self.radius = dp(15)
        self.md_bg_color = self.theme_cls.surfaceContainerHighestColor

        mightBeExpired = (self.playedAt + (60 * 60 * 24)) < time.time()
        self.add_widget(MDBoxLayout( # TODO: Find a way to resize the FitImage widget
            FitImage(
                source = self.gameIconUrl,
                fit_mode = "fill",
                size_hint_y = 1,
                allow_stretch = False,
                radius = [self.radius[0], 0, 0, self.radius[0]]
            ),
            size_hint = (None, 1),
            width = self.height
        ))

        self.add_widget(MDBoxLayout(
            MDBoxLayout(
                FixMDLabel(
                    text = self.gameName,
                    size_hint = (1, None),
                    adaptive_height = True,
                    fontSize = dp(22),
                ),
                FixMDLabel(
                    text = f"{self.gameCreator} • {datetime.fromtimestamp(self.playedAt).strftime('%m/%d/%Y %H:%M')} - {datetime.fromtimestamp(self.leftAt).strftime('%H:%M')}",
                    fontSize = dp(12),
                    adaptive_height = True
                ),
                spacing = dp(-5),
                pos_hint = {"top": 1},
                adaptive_height = True,
                orientation = "vertical",
            ),
            MDButton(
                MDButtonIcon(
                    icon = "play"
                ),
                MDButtonText(
                    text = f"Rejoin {'(might be expired)' if mightBeExpired else ''}"
                ),
                on_press = lambda x: launchRoblox(self.robloxDeeplink),
                style = "filled"
            ),
            spacing = dp(6),
            padding = dp(15),
            adaptive_height = True,
            pos_hint = {"center_y": 0.5},
            orientation = "vertical"
        ))

class PlayLogs(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "Play Logs",
            id = "PlayLogsScreen",
            *args, **kwargs
        )
        self.totalOfPlayLogs = 0
        self.loadPlayLogs()
    
    @scheduleInClock
    def loadPlayLogs(self):
        Logger.debug(TAG + "Loading play logs")
        playLogs = getPlayLogs()
        if not playLogs:
            Logger.debug(TAG + "Not loading play logs as there are none.")
            return
        self.totalOfPlayLogs = len(playLogs)
        Logger.debug(TAG + f"Total of play logs: {self.totalOfPlayLogs}")
        
        universeIdsToRequest = [playLog.universeId for playLog in playLogs]
        Logger.debug(TAG + f"Requesting the following universe ids: {universeIdsToRequest}")
        gameInfosReq = getGameInfo(universeIdsToRequest)
        Logger.debug(TAG + f"Requested game infos: {gameInfosReq}")

        thumbnailsToReq = [
            Thumbnail(
                targetId = playLog.universeId,
                type = "GameIcon",
                size = "512x512",
                isCircular = False
            ) for playLog in playLogs
        ]
        Logger.debug(TAG + f"Requesting the following thumbnails: {thumbnailsToReq}")
        thumbnailsReq = getThumbnails(thumbnailsToReq)
        Logger.debug(TAG + f"Requested thumbnails: {thumbnailsReq}")

        Logger.debug(TAG + "Loading play logs to screen")
        for playSession in playLogs:
            index = playLogs.index(playSession)
            gameInfo: Game = gameInfosReq[index]
            thumbnailUrl = thumbnailsReq[index]

            self.main.add_widget(RecentGamePlayed(
                gameName = gameInfo.name, gameCreator = gameInfo.creator,
                gameIconUrl = thumbnailUrl, playedAt = playSession.playedAt,
                leftAt = playSession.leftAt, robloxDeeplink = playSession.deeplink
            ))
        Logger.debug(TAG + "Done loading")