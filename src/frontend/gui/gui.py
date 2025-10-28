from kivy.logger import Logger
from kivy.properties import BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle
)
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText
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

from backend.rootchecker import suBinaryPath, checkForRootAccess
from .elements import NavigationDrawerItem
from .screens import *

TAG = "DBMainGUI" + ": "

class DroidBloxGUI(MDApp):
    def on_pause(self):
        Logger.debug(TAG, "on_pause()")
        return True

    def on_start(self):
        Logger.info(TAG + "Checking for root access")
        if not checkForRootAccess():
            Logger.error(TAG + "Not given root access or no root, prompting dialog.")
            self.promptNotRooted()
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Darkgreen"

        return MDScreen(
            MDNavigationLayout(MDScreenManager(
                Integrations(),
                # FFlags(),
                # FFlagsEditor(),
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
                    # NavigationDrawerItem(
                    #     icon = "flag",
                    #     text = "FastFlags",
                    #     callback = self._switchScreen
                    # ),
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
    
    def promptNotRooted(self):
        MDDialog(
            MDDialogIcon(
                icon = "alert"
            ),
            MDDialogHeadlineText(
                text = "Root access required"
            ),
            MDDialogSupportingText(
                text = "Your device isn't rooted or you might've not given DroidBlox root access. " \
                        "DroidBlox needs root access in order to apply fast flags and use other features."
            ),
            on_dismiss = lambda *args: self.stop()
        ).open()
    
    def _switchScreen(self, screenToSwitch):
        Logger.debug(TAG + f"Switching screen to {screenToSwitch}")
        self.root.get_ids().ScreenManager.current = screenToSwitch