from kivy.logger import Logger

from backend.apis.discord import getUsername, logout
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
def _onLoginCompleted(token, widget: ExtendedButton):
    global loggingIntoDiscord
    Logger.info(TAG + "Login completed, setting up token")
    settings.writeSetting("token", token)
    loggingIntoDiscord = False

    Logger.debug(TAG + "Setting up username and changing callback")

    username = getUsername(token)
    Logger.info(TAG + f"Logged in as {username}")

    widget.mainTitle.text = "Logout of Discord"
    widget.mainSubtitle.text = f"Logged in as {username}"
    widget.callback = lambda widget: _logoutOfDiscord(widget, token)

def _loginToDiscord(widget: ExtendedButton):
    global loggingIntoDiscord
    if loggingIntoDiscord: return
    loggingIntoDiscord = True

    Logger.info(TAG + f"Logging into discord, attempting to create webview")
    webview = DiscordLoginWebView()
    webview.onLoginCompleted = lambda token: _onLoginCompleted(token, widget)
    
    Logger.debug(TAG + "Starting the webview")
    webview.startWebview()

def _logoutOfDiscord(widget: ExtendedButton, token):
    Logger.info(TAG + "Logging out of discord")
    logout(token)

    Logger.debug(TAG + "Changing callback")
    widget.mainTitle.text = "Login to Discord"
    widget.mainSubtitle.text = "Login to Discord to show your game activity."
    widget.callback = _loginToDiscord

class Integrations(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "Integrations",
            id = "IntegrationsScreen",
            *args, **kwargs
        )

        currentSettings = settings.readSettings()
        self.add_widgets(
            ExtendedButton(
                title = "Launch Roblox",
                subtitle = "Start playing Roblox",
                callback = lambda widget: launchRoblox()
            ),
            SectionText("Activity tracking"),
            ExtendedToggle(
                title = "Enable activity tracking",
                subtitle = "Allow DroidBlox to detect what Roblox game you're playing.",
                callback = lambda value: (
                    settings.writeSetting("enableActivityTracking", value)
                ),
                active = currentSettings["enableActivityTracking"],
                id = "enableActivityTracking"
            ),
            ExtendedToggle(
                title = "Query server location",
                subtitle = "When in-game, you'll be able to see where your server is located.",
                callback = lambda value: (
                    settings.writeSetting("showServerLocation", value)
                ),
                active = currentSettings["showServerLocation"],
                id = "showServerLocation"
            ),
            SectionText("Discord Rich Presence"),
            ExtendedButton(
                title = "Login To Discord" if not currentSettings["token"] else "Logout of Discord",
                subtitle = "Login to discord to show your game activity." if not currentSettings["token"] else f"Logged in as {getUsername(currentSettings['token'])}",
                callback = _loginToDiscord if not currentSettings["token"] else _logoutOfDiscord,
                id = "loginToDiscord"
            ),
            ExtendedToggle(
                title = "Show game activity",
                subtitle = "The Roblox game you're playing will be shown on your Discord profile.",
                callback = lambda value: (
                    settings.writeSetting("showGameActivity", value)
                ),
                active = currentSettings["showGameActivity"],
                id = "showGameActivity"
            ),
            ExtendedToggle(
                title = "Allow activity joining",
                subtitle = "Allows for anybody to join the game you're currently in through your Discord profile.",
                callback = lambda value: (
                    settings.writeSetting("allowActivityJoining", value)
                ),
                active = currentSettings["allowActivityJoining"],
                id = "allowActivityJoining"
            ),
            ExtendedToggle(
                title = "Show Roblox account",
                subtitle = "Shows the Roblox account you're playing with on your Discord profile.",
                callback = lambda value: (
                    settings.writeSetting("showRobloxUser", value)
                ),
                active = currentSettings["showRobloxUser"],
                id = "showRobloxUser"
            )
        )
