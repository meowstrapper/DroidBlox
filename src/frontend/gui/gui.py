from kivy.logger import Logger
from kivy.properties import BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle
)
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerLabel,
    MDNavigationDrawerMenu,
    MDNavigationLayout
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDSharedAxisTransition

from .elements import NavigationDrawerItem
from .screens import *

TAG = "DBMainGUI" + ": "

class DroidBloxGUI(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Darkgreen"

        return MDScreen(
            MDNavigationLayout(MDScreenManager(
                Integrations(),
                FFlags(),
                PlayLogs(),
                About(),
                transition = MDSharedAxisTransition(),
                id = "ScreenManager"
            )),
            MDNavigationDrawer(
                MDNavigationDrawerMenu(
                    MDNavigationDrawerLabel(
                        text = "DroidBlox",
                        font_style = "Headline",
                        role = "small"
                    ),
                    NavigationDrawerItem(
                    icon = "plus",
                    text = "Integrations",
                    callback = self._switchScreen,
                    selected = BooleanProperty(True)
                    ),
                    NavigationDrawerItem(
                        icon = "flag",
                        text = "FastFlags",
                        callback = self._switchScreen
                    ),
                    NavigationDrawerItem(
                        icon = "gamepad-variant",
                        text = "Play Logs",
                        callback = self._switchScreen
                    ),
                    NavigationDrawerItem(
                        icon = "information",
                        text = "About",
                        callback = self._switchScreen
                    )
                ),
                id = "NavigationDrawer"
            )
        )
    def _switchScreen(self, screenToSwitch):
        Logger.debug(TAG + f"Switching screen to {screenToSwitch}")
        self.root.get_ids().ScreenManager.current = screenToSwitch