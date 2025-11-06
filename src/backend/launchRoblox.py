# TODO: Reimplement this in the future

from kivy.logger import Logger
from kivy.utils import platform

from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText
)

from backend.activitywatcher import ActivityWatcherSession
from backend.files import settings, fflags
from backend.threadtools import scheduleInThread

import webbrowser

TAG = "DBLaunchRoblox" + ": "

__all__ = ["launchRoblox"]

if platform == "android":
    from android import mActivity # type: ignore
    from jnius import autoclass, cast, JavaException
    
    currentActivity = cast('android.app.Activity', mActivity)

    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")
    ComponentName = autoclass("android.content.ComponentName")

    @scheduleInClock
    def launchRoblox(deeplinkUrl = "roblox://"):
        Logger.info(TAG + f"Launching roblox with deeplink url: {deeplinkUrl}")

        currentSettings = settings.readSettings()
        
        launchIntent = Intent(Intent.ACTION_VIEW)
        component = ComponentName("com.roblox.client", "com.roblox.client.ActivityProtocolLaunch")
        launchIntent.setComponent(component)
        launchIntent.setData(Uri.parse(deeplinkUrl))

        try:
            Logger.debug(TAG + "Starting intent")
            currentActivity.startActivity(launchIntent)
        except JavaException as e:
            Logger.error(TAG + f"Error while launching intent: {e}. Prompting and not starting.")
            MDDialog(
                MDDialogIcon(
                    icon = "alert"
                ),
                MDDialogHeadlineText(
                    text = "Roblox isn't installed"
                ),
                MDDialogSupportingText(
                    text = "Cannot find Roblox in this device. Make sure it's properly installed."
                )
            ).open()
            return
        
        if currentSettings["enableActivityTracking"]:
            Logger.info(TAG + "Starting activity tracker")
            ActivityWatcherSession().start()
else:
    Logger.info(TAG + f"Running on {platform}, not importing.")