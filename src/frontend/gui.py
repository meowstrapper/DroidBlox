"""
GUI for DroidBlox, licensed in GNU GPL v2.0
https://github.com/meowstrapper/DroidBlox/blob/main/LICENSE
"""

from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.logger import Logger, LOG_LEVELS
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
#from kivy.uix.codeinput import CodeInput

from kivymd.app import MDApp
from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle
)
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import BaseButton, MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogIcon,
    MDDialogSupportingText
)
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
    MDNavigationDrawerLabel,
    MDNavigationDrawerMenu,
    MDNavigationLayout
)
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField
from kivymd.uix.transition import MDSharedAxisTransition

from . import webview
from backend import activitywatcher
from backend.threadtools import scheduleInClock
from backend.apis import roblox, discord
from backend.files import fflags, playlogs, settings

import sys
import time
import webbrowser

from datetime import datetime
from typing import Any, Callable, List

TAG = "DroidBloxGUI" + ": "

class BasicScreen(MDScreen):
    name = StringProperty()
    navDrawer: MDNavigationDrawer = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.main = MDBoxLayout(
            *args,
            padding = dp(15),
            spacing = dp(15),
            orientation = "vertical",
            adaptive_height = True
        )

        self.add_widget(MDBoxLayout(
            MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon = "menu",
                        on_release = self._closeDrawer
                    )
                ),
                MDTopAppBarTitle(
                    text = self.name
                )
            ),
            MDScrollView(
                self.main,
                do_scroll_x = False
            ),
            orientation = "vertical"
        ))

    def _closeDrawer(self, *args):
        self.navDrawer.set_state("open")

class FixMDLabel(MDLabel):
    fontSize = NumericProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_size = self.fontSize

class SectionText(MDLabel):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text = text, bold = True, font_style = "Label", *args, **kwargs)
        self.adaptive_size = True
        self.text_color = self.theme_cls.primaryColor

# lmao wtf should i call it
class IconWithTextDetails(MDBoxLayout): # inspired by kizzy lol
    icon = StringProperty()
    title = StringProperty()
    subtitle = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ripple_behavior = True
        self.spacing = dp(15)
        self.size_hint = (1, None)
        self.adaptive_height = True

        if self.icon:
            iconToSet = MDIcon(
                icon = self.icon,
                icon_color = self.theme_cls.primaryColor,
                pos_hint = {"center_y": 0.5 }
            )
            iconToSet.font_size = dp(25)
            self.add_widget(iconToSet)
        
        self.mainTitle = FixMDLabel(
            text = self.title,
            font_style = "Title",
            fontSize = dp(19),
            adaptive_height = True
        )
        self.mainSubtitle = MDLabel(
            text = self.subtitle,
            markup = True,
            on_ref_press = lambda instance, url: webbrowser.open(url),
            font_style = "Label",
            role = "medium",
            adaptive_height = True
        )
        self.add_widget(
            MDBoxLayout(
                self.mainTitle, self.mainSubtitle,
                pos_hint = {"center_y": 0.5},
                adaptive_height = True,
                spacing = -5,
                orientation = "vertical",
            )
        )

class ExtendedButton(RectangularRippleBehavior, IconWithTextDetails):
    callback = ObjectProperty(lambda: ...)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def start_ripple(self): # TODO: improve this
        mainthread(self.callback)()
        super().start_ripple()
    

class ExtendedToggle(IconWithTextDetails):
    callback: Callable[[bool], None] = ObjectProperty(lambda x: None) # epllipsis doesnt work?

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = MDSwitch(
            on_release = lambda x: self.callback(not x.active),
            pos_hint = {"center_y": 0.5}
        )
        self.add_widget(self.main)

class ExtendedTextField(IconWithTextDetails):
    callback: Callable[[str], None] = ObjectProperty(lambda x: None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = MDTextField(
            mode = "outlined",
            pos_hint = {"center_y": 0.5},
            size_hint_x = 0.2,
            size_hint_y = 1
        )
        self.main.bind(focus=lambda _, focus: (
            self.callback(self.main.text) if not focus else None
        ))
        self.add_widget(self.main)

class DropdownItem:
    def __init__(self, text: str, onRelease: Callable[[str], None] = lambda: ...):
        self.text = text
        self.on_release = onRelease

class ExtendedDropdown(IconWithTextDetails):
    items: List[DropdownItem] = ObjectProperty()
    default: str = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropItemMenu: MDDropdownMenu = None
        self.dropDownItemText = MDDropDownItemText(text = self.default)
        self.add_widget(
            MDDropDownItem(
                self.dropDownItemText,
                pos_hint = {"center_y": 0.5},
                on_release = self._openMenu
            )
        )
    
    def _openMenu(self, caller):
        if not self.dropItemMenu:
            self.items = [{"text": i.text, "on_release": lambda item=i: self._menuCallback(item.text, item.on_release)} for i in self.items]
            self.dropItemMenu = MDDropdownMenu(
                caller = caller, items = self.items
            )
        self.dropItemMenu.open()
    
    def _menuCallback(self, text: str, originalCallback):
        originalCallback()

        self.dropDownItemText.text = text
        self.dropItemMenu.dismiss()

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
        self.height = dp(120)
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
                    fontSize = dp(24),
                ),
                FixMDLabel(
                    text = f"{self.gameCreator} • {datetime.fromtimestamp(self.playedAt).strftime('%m/%d/%Y %H:%M')} - {datetime.fromtimestamp(self.leftAt).strftime('%H:%M')}",
                    fontSize = dp(16),
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
                on_release = lambda x: webbrowser.open(self.robloxDeeplink),
                style = "filled"
            ),
            spacing = dp(6),
            padding = dp(15),
            size_hint = (1, 1),
            orientation = "vertical"
        ))

class NavigationDrawerItem(MDNavigationDrawerItem):
    icon = StringProperty()
    text = StringProperty()
    callback: Callable[[str], None] = ObjectProperty(lambda x: ...)

    def _closeDrawerAndCall(self):
        self.parent.parent.parent.set_state("closed")
        self.callback(self.text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_release = self._closeDrawerAndCall
        self.add_widget(
            MDNavigationDrawerItemLeadingIcon(
                icon = self.icon
            )
        )
        self.add_widget(
            MDNavigationDrawerItemText(
                text = self.text
            )
        )

class DroidBloxGUI(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ScreenManager: MDScreenManager = None
        self.NavigationDrawer: MDNavigationDrawer = None

        self.loggingInToDiscord = False
    
    def on_start(self):
        #self.promptRobloxIsntInstalled()
        self.loadPlayLogs()
        self.loadFFlags()
        self.loadSettings()

        discordToken = settings.readSettings()["token"]
        if discordToken: self.applyDiscordUsernameWithToken(discordToken)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Darkgreen"

        self.NavigationDrawer = MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerLabel(
                    text = "DroidBlox",
                    font_style = "Headline",
                    role = "small"
                ),
                NavigationDrawerItem(
                    icon = "plus",
                    text = "Integrations",
                    callback = self.switchScreen,
                    selected = BooleanProperty(True)
                ),
                NavigationDrawerItem(
                    icon = "flag",
                    text = "FastFlags",
                    callback = self.switchScreen
                ),
                NavigationDrawerItem(
                    icon = "gamepad-variant",
                    text = "Play Logs",
                    callback = self.switchScreen
                ),
                NavigationDrawerItem(
                    icon = "information",
                    text = "About",
                    callback = self.switchScreen
                )
            )
        )
        self.ScreenManager = MDScreenManager(
            BasicScreen( # INTEGRATIONS
                ExtendedButton(
                    title = "Launch Roblox",
                    subtitle = "Start playing Roblox",
                    callback = self._launchRoblox
                ),
                SectionText("Activity tracking"),
                ExtendedToggle(
                    title = "Enable activity tracking",
                    subtitle = "Allow DroidBlox to detect what Roblox game you're playing.",
                    callback = lambda value: (
                        settings.writeSetting("enableActivityTracking", value)
                    ),
                    id = "enableActivityTracking"
                ),
                ExtendedToggle(
                    title = "Query server location",
                    subtitle = "When in-game, you'll be able to see where your server is located.",
                    callback = lambda value: (
                        settings.writeSetting("showServerLocation", value)
                    ),
                    id = "showServerLocation"
                ),
                SectionText("Discord Rich Presence"),
                ExtendedButton(
                    title = "Login To Discord",
                    subtitle = "Login to discord to show your game activity.",
                    callback = self._loginToDiscord,
                    id = "loginToDiscord"
                ),
                ExtendedToggle(
                    title = "Show game activity",
                    subtitle = "The Roblox game you're playing will be shown on your Discord profile.",
                    callback = lambda value: (
                        settings.writeSetting("showGameActivity", value)
                    ),
                    id = "showGameActivity"
                ),
                ExtendedToggle(
                    title = "Allow activity joining",
                    subtitle = "Allows for anybody to join the game you're currently in through your Discord profile.",
                    callback = lambda value: (
                        settings.writeSetting("allowActivityJoining", value)
                    ),
                    id = "allowActivityJoining"
                ),
                ExtendedToggle(
                    title = "Show Roblox account",
                    subtitle = "Shows the Roblox account you're playing with on your Discord profile.",
                    callback = lambda value: (
                        settings.writeSetting("showRobloxUser", value)
                    ),
                    id = "showRobloxUser"
                ),
                navDrawer = self.NavigationDrawer,
                name = "Integrations",
                id = "IntegrationsScreen",
                md_bg_color = self.theme_cls.backgroundColor
            ),
            BasicScreen( # FAST FLAGS
                SectionText("Advanced"),
                ExtendedButton(
                    icon = "pencil",
                    title = "Fast Flag Editor",
                    subtitle = "Manage your own Fast Flags. Use with caution. (COMING NEXT UPDATE)",
                    callback = lambda: (
                        Logger.warning(TAG + "haiii:3333")
                    )
                ),
                ExtendedToggle(
                    title = "Allow DroidBlox to manage Fast Flags",
                    subtitle = "Disabling this will prevent anything configured here from being applied to Roblox.",
                    callback = lambda value: (
                        settings.writeSetting("applyFFlags", value)
                    ),
                    id = "applyFFlags"
                ),
                SectionText("Presets"),
                ExtendedToggle(
                    title = "Disable Roblox telemetry",
                    subtitle = "Note this disables only some of the Roblox telemetry.",
                    callback = lambda value: (
                        fflags.mergeFFlags({
                            "FFlagDebugDisableTelemetryEphemeralCounter": "True",
                            "FFlagDebugDisableTelemetryEphemeralStat": "True",
                            "FFlagDebugDisableTelemetryEventIngest": "True",
                            "FFlagDebugDisableTelemetryV2Counter": "True",
                            "FFlagDebugDisableTelemetryV2Event": "True",
                            "FFlagDebugDisableTelemetryV2Stat": "True"
                        }) if value else fflags.deleteFFlags([
                            "FFlagDebugDisableTelemetryEphemeralCounter",
                            "FFlagDebugDisableTelemetryEphemeralStat",
                            "FFlagDebugDisableTelemetryEventIngest",
                            "FFlagDebugDisableTelemetryV2Counter",
                            "FFlagDebugDisableTelemetryV2Event",
                            "FFlagDebugDisableTelemetryV2Stat"
                        ])
                    ),
                    id = "disableRobloxTelemetry"
                ),
                SectionText("Rendering and Graphics"),
                ExtendedDropdown(
                    title = "Anti-aliasing quality (MSAA)",
                    subtitle = "Smoothens the jagged edges to make textures detailed. This may impact your gaming experience depending on your device.",
                    items = [
                        DropdownItem("Automatic", onRelease = lambda: (
                            fflags.deleteFFlags(["FIntDebugForceMSAASamples"])
                        )),
                        DropdownItem("1x", onRelease = lambda: (
                            fflags.writeFFlag("FIntDebugForceMSAASamples", "1")
                        )),
                        DropdownItem("2x", onRelease = lambda: (
                            fflags.writeFFlag("FIntDebugForceMSAASamples", "2")
                        )), 
                        DropdownItem("4x", onRelease = lambda: (
                            fflags.writeFFlag("FIntDebugForceMSAASamples", "4")
                        ))
                    ],
                    default = "Automatic",
                    id = "antiAliasingQuality"
                ),
                ExtendedToggle(
                    title = "Disable player shadows",
                    subtitle = "Disables the shadow on players.",
                    callback = lambda value: (
                        fflags.writeFFlag("FIntRenderShadowIntensity", 0) if value else fflags.deleteFFlags(["FIntRenderShadowIntensity"])
                    ),
                    id = "disablePlayerShadows"
                ),
                ExtendedToggle(
                    title = "Disable post-processing effects",
                    subtitle = "Disables post-processing effects (e.g. sun rays, depth of field element, etc). " +
                                self.createRef("https://create.roblox.com/docs/environment/post-processing-effects"),
                    callback = lambda value: (
                        fflags.writeFFlag("FFlagDisablePostFx", "True") if value else fflags.deleteFFlags(["FFlagDisablePostFx"])
                    ),
                    id = "disablePostProcessingEffects"
                ),
                ExtendedToggle(
                    title = "Disable terrain textures",
                    subtitle = "Dont render terrain textures",
                    callback = lambda value: (
                        fflags.writeFFlag("FIntTerrainArraySliceSize", "0") if value else fflags.deleteFFlags(["FIntTerrainArraySliceSize"])
                    ),
                    id = "disableTerrainTextures"
                ),
                ExtendedTextField(
                    title = "Framerate limit",
                    subtitle = "Set the framerate limit for Roblox. " +
                                self.createRef("https://github.com/bloxstraplabs/bloxstrap/wiki/A-guide-to-FastFlags#framerate-limit"),
                    callback = lambda value: (
                        fflags.writeFFlag("DFIntTaskSchedulerTargetFps", value) if value else fflags.deleteFFlags(["DFIntTaskSchedulerTargetFps"])
                    ),
                    id = "framerateLimit"
                ),
                ExtendedDropdown(
                    title = "Preferred lighting technology",
                    subtitle = "Choose which lighting technology should be forced in games. Might cause lighting issues! " +
                                self.createRef("https://github.com/bloxstraplabs/bloxstrap/wiki/A-guide-to-FastFlags#preferred-lighting-technology"),
                    items = [
                        DropdownItem("Chosen by game", onRelease = lambda: (
                            fflags.deleteFFlags([
                                "DFFlagDebugRenderForceTechnologyVoxel",
                                "FFlagDebugForceFutureIsBrightPhase2",
                                "FFlagDebugForceFutureIsBrightPhase3"
                            ])
                        )),
                        DropdownItem("Voxel (Phase 1)", onRelease = lambda: (
                            fflags.writeFFlag("DFFlagDebugRenderForceTechnologyVoxel", True),
                            fflags.deleteFFlags([
                                "FFlagDebugForceFutureIsBrightPhase2",
                                "FFlagDebugForceFutureIsBrightPhase3"
                            ])
                        )),
                        DropdownItem("Shadow Map (Phase 2)", onRelease = lambda: (
                            fflags.writeFFlag("FFlagDebugForceFutureIsBrightPhase2", True),
                            fflags.deleteFFlags([
                                "DFFlagDebugRenderForceTechnologyVoxel",
                                "FFlagDebugForceFutureIsBrightPhase3"
                            ])
                        )),
                        DropdownItem("Future (Phase 3), ", onRelease = lambda: (
                            fflags.writeFFlag("FFlagDebugForceFutureIsBrightPhase3", True),
                            fflags.deleteFFlags([
                                "FFlagDebugForceFutureIsBrightPhase2",
                                "DFFlagDebugRenderForceTechnologyVoxel"
                            ])
                        ))
                    ],
                    default = "Chosen by game",
                    id = "preferredLightingTechnology"
                ),
                ExtendedDropdown(
                    title = "Rendering mode",
                    subtitle = "Choose what rendering api to use for Roblox",
                    items = [
                        DropdownItem("Automatic", onRelease = lambda: (
                            fflags.deleteFFlags([
                                "FFlagDebugGraphicsPreferVulkan",
                                "FFlagDebugGraphicsPreferOpenGL"
                            ])
                        )),
                        DropdownItem("Vulkan", onRelease = lambda: (
                            fflags.writeFFlag("FFlagDebugGraphicsPreferVulkan", "True"),
                            fflags.deleteFFlags(["FFlagDebugGraphicsPreferOpenGL"])
                        )),
                        DropdownItem("OpenGL", onRelease = lambda: (
                            fflags.writeFFlag("FFlagDebugGraphicsPreferOpenGL", "True"),
                            fflags.deleteFFlags(["FFlagDebugGraphicsPreferVulkan"])
                        )),
                    ],
                    default = "Automatic",
                    id = "renderingMode"
                ),
                ExtendedDropdown(
                    title = "Texture quality",
                    subtitle = "Choose what level of texture quality to render",
                    items = [
                        DropdownItem("Automatic", onRelease = lambda: (
                            fflags.deleteFFlags([
                                "DFFlagTextureQualityOverrideEnabled",
                                "DFIntTextureQualityOverride"
                            ])
                        )),
                        DropdownItem("Level 0 (lowest)", onRelease = lambda: (
                            fflags.mergeFFlags({
                                "DFFlagTextureQualityOverrideEnabled": "True",
                                "DFIntTextureQualityOverride": "0"
                            })
                        )),
                        DropdownItem("Level 1 ", onRelease = lambda: (
                            fflags.mergeFFlags({
                                "DFFlagTextureQualityOverrideEnabled": "True",
                                "DFIntTextureQualityOverride": "1"
                            })
                        )),
                        DropdownItem("Level 2", onRelease = lambda: (
                            fflags.mergeFFlags({
                                "DFFlagTextureQualityOverrideEnabled": "True",
                                "DFIntTextureQualityOverride": "2"
                            })
                        )),
                        DropdownItem("Level 3 (highest)", onRelease = lambda: (
                            fflags.mergeFFlags({
                                "DFFlagTextureQualityOverrideEnabled": "True",
                                "DFIntTextureQualityOverride": "3"
                            })
                        ))
                    ],
                    default = "Automatic",
                    id = "textureQuality"
                ),
                SectionText("User Interface and Layout"),
                ExtendedTextField(
                    title = "Hiding GUIs",
                    subtitle = "Toggled with " + self.createRef("https://bloxstraplabs.com/wiki/features/engine-settings/#gui-hiding", "keyboard shortcuts (might require using an OTG).") +
                                " Input id of a group you're in.",
                    callback = lambda value: (
                        fflags.mergeFFlags({
                            "DFIntCanHideGuiGroupId": value,
                            "FFlagUserShowGuiHideToggles": True
                        }) if value else fflags.deleteFFlags([
                            "DFIntCanHideGuiGroupId",
                            "FFlagUserShowGuiHideToggles"
                        ])
                    ),
                    id = "hideGui"
                ),
                ExtendedTextField(
                    title = "Font size",
                    subtitle = "Default is 1",
                    callback = lambda value: (
                        fflags.writeFFlag("FIntFontSizePadding", value) if value else fflags.deleteFFlags(["FIntFontSizePadding"])
                    ),
                    id = "fontSize"
                ),
                SectionText("Debloat Roblox Menu"),
                ExtendedToggle(
                    title = "VR Toggle",
                    subtitle = "Remove VR Toggle",
                    callback = lambda value: (
                        fflags.writeFFlag("FFlagAlwaysShowVRToggleV3", "False") if value else fflags.deleteFFlags(["FFlagAlwaysShowVRToggleV3"])
                    ),
                    id = "removeVrToggle"
                ),
                ExtendedToggle(
                    title = "Feedback button",
                    subtitle = "Remove Feedback button",
                    callback = lambda value: (
                        fflags.writeFFlag("FFlagDisableFeedbackSoothsayerCheck", "True") if value else fflags.removeFFlags(["FFlagDisableFeedbackSoothsayerCheck"])
                    ),
                    id = "removeFeedbackButton"
                ),
                ExtendedToggle(
                    title = "Language selector",
                    subtitle = "Remove Language selector",
                    callback = lambda value: (
                        fflags.writeFFlag("FIntV1MenuLanguageSelectionFeaturePerMillageRollout", "0") if value else fflags.removeFFlags(["FIntV1MenuLanguageSelectionFeaturePerMillageRollout"])
                    ),
                    id = "removeLanguageSelector"
                ),
                ExtendedToggle(
                    title = "Framerate cap",
                    subtitle = "Remove Framerate cap",
                    callback = lambda value: (
                        fflags.writeFFlag("FFlagGameBasicSettingsFramerateCap5", "False") if value else fflags.removeFFlags(["FFlagGameBasicSettingsFramerateCap5"])
                    ),
                    id = "removeFramerateCap"
                ),
                ExtendedToggle(
                    title = "Chat translation",
                    subtitle = "Remove Chat translation",
                    callback = lambda value: (
                        fflags.writeFFlag("FFlagChatTranslationSettingEnabled3", "False") if value else fflags.removeFFlags(["FFlagChatTranslationSettingEnabled3"])
                    ),
                    id = "removeChatTranslation"
                ),
                SectionText("FLog Debug"),
                ExtendedTextField(
                    title = "Flag State",
                    subtitle = "Show values of specified flags during runtime. Each flag is comma separated.",
                    callback = lambda value: (
                        fflags.writeFFlag("FStringDebugShowFlagState", value) if value else fflags.deleteFFlags(["FStringDebugShowFlagState"])
                    ),
                    id = "flagState"
                ),
                ExtendedToggle(
                    title = "Ping breakdown",
                    subtitle = "Sends ping information to the Roblox console.",
                    callback = lambda value: (
                        fflags.writeFFlag("DFFlagDebugPrintDataPingBreakDown", "False") if value else fflags.removeFFlags(["DFFlagDebugPrintDataPingBreakDown"])
                    ),
                    id = "pingBreakdown"
                ),
                name = "FastFlags",
                navDrawer = self.NavigationDrawer,
                id = "FastFlagsScreen",
                md_bg_color = self.theme_cls.backgroundColor
            ),
            BasicScreen(
                name = "Play Logs",
                navDrawer = self.NavigationDrawer,
                id = "PlayLogsScreen",
                md_bg_color = self.theme_cls.backgroundColor
            ),
            BasicScreen(
                MDBoxLayout(
                    FitImage(
                        source = "https://github.com/meowstrapper/DroidBlox/blob/main/assets/icon.png?raw=true",
                        fit_mode = "scale-down"
                    ),
                    size_hint = (1, None),
                    height = dp(150)
                ),
                FixMDLabel(
                    text = "DroidBlox is a bootstrapper for Roblox's android client that gives you additional features.\n\n" \
                            f"It is a {self.createRef('https://github.com/bloxstraplabs/bloxstrap', 'Bloxstrap')} alternative to android except there are some features that are [b]not currently possible[/b] in the android version.\n\n" +
                            self.createRef("https://github.com/meowstrapper/DroidBlox/blob/main/LICENSE", "License") + "\n" +
                            self.createRef("https://github.com/meowstrapper/DroidBlox", "GitHub Repo") + "\n" +
                            self.createRef("https://discord.gg/kVmH76umHv", "Discord Server") + "\n" +
                            self.createRef("https://github.com/meowstrapper/DroidBlox?tab=readme-ov-file#credits", "Credits") + "\n" +
                            self.createRef("https://github.com/meowstrapper/DroidBlox?tab=readme-ov-file#licenses-libraries-used-and-codes-that-i-refactored-or-used", "Licenses") + "\n",
                    on_ref_press = lambda instance, url: webbrowser.open(url),
                    markup = True,
                    adaptive_height = True,
                    fontSize = dp(17),
                    halign = "center"
                ),

                name = "About",
                navDrawer = self.NavigationDrawer,
                id = "AboutScreen",
                md_bg_color = self.theme_cls.backgroundColor
            ),
            transition = MDSharedAxisTransition()
        )

        return MDScreen(
            MDNavigationLayout(self.ScreenManager),
            self.NavigationDrawer
        )
    
    @scheduleInClock
    def switchScreen(self, screenToSwitch: str, *args):
        Logger.debug(TAG + f"Switching screen to {screenToSwitch}")
        self.ScreenManager.current = screenToSwitch
    
    @scheduleInClock
    def promptRobloxIsntInstalled(self):
        dialog = MDDialog(
            MDDialogIcon(icon = "alert"),
            MDDialogHeadlineText(text = "Roblox isn't installed"),
            MDDialogSupportingText(
                text = "Roblox couldn't be found in this device. Make sure you have Roblox installed."
            )
        )
        dialog.open()
        while dialog._is_open: ...
    
    @scheduleInClock
    def promptRootAccessRequired(self):
        dialog = MDDialog(
            MDDialogIcon(icon = "alert"),
            MDDialogHeadlineText(text = "Root access required!"),
            MDDialogSupportingText(
                text = "Please give DroidBlox root access in order to use features like fast flags and activity watcher."
            )
        )
        dialog.open()
        while dialog._is_open: ...

    @scheduleInClock
    def promptDeviceIsntRooted(self):
        dialog = MDDialog(
            MDDialogIcon(icon = "alert"),
            MDDialogHeadlineText(text = "This device isn't rooted"),
            MDDialogSupportingText(
                text = "This device seems to not be rooted, DroidBlox needs root to access Roblox's files for it's features. If you're rooted and think this is a false alarm, join our discord server and get support."
            ),
            on_dismiss = lambda: (
                Logger.info(TAG + "Exiting app after dismissing not rooted device prompt"),
                sys.exit()
            )
        )
        dialog.open()
        while dialog._is_open: ...
    
    @scheduleInClock
    def loadSettings(self, *args):
        Logger.debug(TAG + "Loading setting-based gui elements")
        timeStarted = time.time()

        IntegrationsScreen = self.ScreenManager.get_ids().IntegrationsScreen.main.get_ids()
        FastFlagsScreen = self.ScreenManager.get_ids().FastFlagsScreen.main.get_ids()
        currentSettings = settings.readSettings()

        IntegrationsScreen.enableActivityTracking.main.active = currentSettings["enableActivityTracking"]
        IntegrationsScreen.showServerLocation.main.active = currentSettings["showServerLocation"]
        IntegrationsScreen.showGameActivity.main.active = currentSettings["showGameActivity"]
        IntegrationsScreen.allowActivityJoining.main.active = currentSettings["allowActivityJoining"]
        IntegrationsScreen.showRobloxUser.main.active = currentSettings["showRobloxUser"]
        FastFlagsScreen.applyFFlags.main.active = currentSettings["applyFFlags"]

        timeEnded = time.time()
        Logger.debug(TAG + f"Loading settings took {timeEnded - timeStarted}")

    @scheduleInClock
    def loadFFlags(self, *args):
        Logger.debug(TAG + "Loading fflag-based gui elements")
        timeStarted = time.time()

        FastFlagsScreen = self.ScreenManager.get_ids().FastFlagsScreen.main.get_ids()
        currentFFlags = fflags.readFFlags()
        if not currentFFlags: return

        # is there a better way to do this? dont hate this because i made this at like 11pm to 12am
        if "FFlagDebugDisableTelemetryEphemeralCounter" in currentFFlags:
            FastFlagsScreen.disableRobloxTelemetry.main.active = True
        if "FIntDebugForceMSAASamples" in currentFFlags:
            FastFlagsScreen.antiAliasingQuality.dropDownItemText.text = {
                "1": "1x",
                "2": "2x",
                "4": "4x"
            }[str(currentFFlags["FIntDebugForceMSAASamples"])]
        if "FIntRenderShadowIntensity" in currentFFlags:
            FastFlagsScreen.disablePlayerShadows.main.active = True
        if "FFlagDisablePostFx" in currentFFlags:
            FastFlagsScreen.disablePostProcessingEffects.main.active = True
        if "FIntTerrainArraySliceSize" in currentFFlags:
            FastFlagsScreen.disableTerrainTextures.main.active = True
        if "DFIntTaskSchedulerTargetFps" in currentFFlags:
            FastFlagsScreen.framerateLimit.main.text = currentFFlags["DFIntTaskSchedulerTargetFps"]
        if "DFFlagDebugRenderForceTechnologyVoxel" in currentFFlags:
            FastFlagsScreen.preferredLightingTechnology.dropDownItemText.text = "Voxel (Phase 1)"
        if "FFlagDebugForceFutureIsBrightPhase2" in currentFFlags:
            FastFlagsScreen.preferredLightingTechnology.dropDownItemText.text = "Shadow Map (Phase 2)"
        if "FFlagDebugForceFutureIsBrightPhase3" in currentFFlags:
            FastFlagsScreen.preferredLightingTechnology.dropDownItemText.text = "Future (Phase 3)"
        if "FFlagDebugGraphicsPreferVulkan" in currentFFlags:
            FastFlagsScreen.renderingMode.dropDownItemText.text = "Vulkan"
        if "FFlagDebugGraphicsPreferOpenGL" in currentFFlags:
            FastFlagsScreen.renderingMode.dropDownItemText.text = "OpenGL"
        if "DFIntTextureQualityOverride" in currentFFlags:
            FastFlagsScreen.textureQuality.dropDownItemText.text = {
                "0": "Level 0 (lowest)",
                "1": "Level 1",
                "2": "Level 2",
                "3": "Level 3 (highest)",
            }[str(currentFFlags["DFIntTextureQualityOverride"])]
        if "DFIntCanHideGuiGroupId" in currentFFlags:
            FastFlagsScreen.hideGui.main.text = currentFFlags["DFIntCanHideGuiGroupId"]
        if "FIntFontSizePadding" in currentFFlags:
            FastFlagsScreen.fontSize.main.text = currentFFlags["FIntFontSizePadding"]
        if "FFlagAlwaysShowVRToggleV3" in currentFFlags:
            FastFlagsScreen.disablePlayerShadows.main.active = True
        if "FFlagDisableFeedbackSoothsayerCheck" in currentFFlags:
            FastFlagsScreen.removeFeedbackButton.main.active = True
        if "FIntV1MenuLanguageSelectionFeaturePerMillageRollout" in currentFFlags:
            FastFlagsScreen.removeLanguageSelector.main.active = True
        if "FFlagGameBasicSettingsFramerateCap5" in currentFFlags:
            FastFlagsScreen.removeFramerateCap.main.active = True
        if "FFlagChatTranslationSettingEnabled3" in currentFFlags:
            FastFlagsScreen.removeChatTranslation.main.active = True
        if "FStringDebugShowFlagState" in currentFFlags:
            FastFlagsScreen.flagState.main.text = currentFFlags["FStringDebugShowFlagState"]
        if "DFFlagDebugPrintDataPingBreakDown" in currentFFlags:
            FastFlagsScreen.pingBreakdown.main.active = True
        
        timeEnded = time.time()
        Logger.debug(TAG + f"Loading fflags took {timeEnded - timeStarted}s")

    @scheduleInClock
    def loadPlayLogs(self, *args):
        Logger.debug(TAG + "Loading play logs")
        timeStarted = time.time()

        PlayLogsScreen: MDBoxLayout = self.ScreenManager.get_ids().PlayLogsScreen.main
        currentPlayLogs = playlogs.getPlayLogs()
        if not currentPlayLogs: return

        chunksOfPlaySessions = [currentPlayLogs[i:i + 100] for i in range(0, len(currentPlayLogs), 100)]
        for playSessions in chunksOfPlaySessions:
            gameInfosReq = roblox.getGameInfo([playSession.universeId for playSession in playSessions])
            Logger.debug(TAG + f"Requested game infos: {gameInfosReq}")

            thumbnailsReq = roblox.getThumbnails([roblox.models.Thumbnail(
                targetId = playSession.universeId,
                type = "GameIcon",
                size = "512x512",
                isCircular = False
            ) for playSession in playSessions])
            Logger.debug(TAG + f"Requested thumbnails: {thumbnailsReq}")
            
            for playSession in playSessions:
                index = playSessions.index(playSession)

                gameInfo = gameInfosReq[index]
                thumbnailUrl = thumbnailsReq[index]
                PlayLogsScreen.add_widget(RecentGamePlayed(
                    gameName = gameInfo.name, gameCreator = gameInfo.creator,
                    gameIconUrl = thumbnailUrl, playedAt = playSession.playedAt,
                    leftAt = playSession.leftAt, robloxDeeplink = playSession.deeplink
                ))
        
        timeEnded = time.time()
        Logger.debug(TAG + f"Loading play logs took {timeEnded - timeStarted}s")

    @scheduleInClock
    def applyDiscordUsernameWithToken(self, token: str):
        IntegrationsScreen = self.ScreenManager.get_ids().IntegrationsScreen.main.get_ids()

        Logger.debug(TAG + "Trying to get discord username from token")
        username = discord.getUsername(token)
        if not username:
            Logger.error(TAG + "Something went wrongg!!! Not applying username to gui")
            return
        
        Logger.debug(TAG + f"Username is {username}, changing text and callback")
        IntegrationsScreen.loginToDiscord.mainTitle.text = "Logout of Discord"
        IntegrationsScreen.loginToDiscord.mainSubtitle.text = f"You're currently logged in as {username}"
        IntegrationsScreen.loginToDiscord.callback = self._logoutOfDiscord
    
    @scheduleInClock
    def _loginToDiscord(self):
        if self.loggingInToDiscord: return
        self.loggingInToDiscord = True
        
        Logger.debug(TAG + f"Logging in to discord, attempting to create webview")
        wv = webview.DiscordLoginWebView()
        wv.onLoginCompleted = lambda token: (
            Logger.debug(TAG + f"Login completed, setting up token"),
            settings.writeSetting("token", token),
            self.applyDiscordUsernameWithToken(token),
            self.__setattr__("loggingInToDiscord", False)
        )
        Logger.debug(TAG + f"Starting the webview")
        wv.startWebview()

    @scheduleInClock
    def _logoutOfDiscord(self):
        IntegrationsScreen = self.ScreenManager.get_ids().IntegrationsScreen.main.get_ids()

        Logger.debug(TAG + "Logging out of discord and going back to the normal callback and text")
        discord.logout(settings.readSettings()["token"])
        settings.writeSetting("token", "")

        IntegrationsScreen.loginToDiscord.mainTitle.text = "Login to Discord"
        IntegrationsScreen.loginToDiscord.mainSubtitle.text = "Login to discord to show your game activity."
        IntegrationsScreen.loginToDiscord.callback = self._loginToDiscord
    
    @scheduleInClock
    def _launchRoblox(self):
        currentSettings = settings.readSettings()
        Logger.info(TAG + f"Launching Roblox")
        webbrowser.open("roblox://")
        if currentSettings["applyFFlags"]:
            fflags.applyFFlagsToRoblox()
        if currentSettings["enableActivityTracking"]:
            activityWatcher = activitywatcher.ActivityWatcherSession()
            Logger.debug(TAG + "Starting activity watcher")
            activityWatcher.start()

    def createRef(self, url, text = "Learn more."):
        primaryColor = self.theme_cls.primaryColor
        r = round(primaryColor[0] * 255)
        g = round(primaryColor[1] * 255)
        b = round(primaryColor[2] * 255)
        hex = f"#{r:02X}{g:02X}{b:02X}"
        return f"[ref={url}][color={hex}][u]{text}[/u][/color][/ref]"