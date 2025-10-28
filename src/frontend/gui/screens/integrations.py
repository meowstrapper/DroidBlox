from kivy.logger import Logger

from backend.files import settings
from frontend.gui.elements import (
    ExtendedButton,
    SectionText,
    BasicScreen,
    ExtendedToggle
)

TAG = "DBIntegrationsScreen" + ": "

__all__ = ["Integrations"]

try:
    # for testing purposes (e.g., not testing on android)
    from frontend.webview import DiscordLoginWebView
    from backend.launchRoblox import launchRoblox
except:
    Logger.debug(TAG + "Not importing DiscordLoginWebview and launchRoblox")
    def launchRoblox(): ...

loggingIntoDiscord = False
def _onLoginCompleted(token):
    Logger.debug(TAG + "Login completed, se_loginTotting up token")
    settings.writeSetting("token", token)
    loggingIntoDiscord = False

def _loginToDiscord():
    if loggingIntoDiscord: return
    loggingIntoDiscord = True

    Logger.debug(TAG + f"Logging into discord, attempting to create webview")
    webview = DiscordLoginWebView()
    webview.onLoginCompleted = _onLoginCompleted
    
    Logger.debug(TAG + "Starting the webview")
    webview.startWebview()

class Integrations(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "Integrations",
            id = "IntegrationsScreen",
            *args, **kwargs
        )
        self.add_widgets(
            ExtendedButton(
                title = "Launch Roblox",
                subtitle = "Start playing Roblox",
                callback = launchRoblox
            ),
            SectionText("Activity tracking"),
            ExtendedButton(
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
                callback = _loginToDiscord,
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
            )
        )
