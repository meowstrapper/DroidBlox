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

import webbrowser

TAG = "DBLaunchRoblox" + ": "

__all__ = ["launchRoblox"]

if platform == "android":
    from android import mActivity # type: ignore
    from jnius import autoclass, cast
    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")

    def launchRoblox(deeplinkUrl = "roblox://"):
        Logger.info(TAG + f"Launching roblox with deeplink url: {deeplinkUrl}")

        currentSettings = settings.readSettings()
        currentActivity = cast('android.app.Activity', mActivity)
        launchIntent = currentActivity.getPackageManager().getLaunchIntentForPackage("com.roblox.client")

        if not launchIntent:
            Logger.error(TAG + "launchIntent is None! Prompting and not starting.")
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
        
        # if currentSettings["applyFFlags"]:
        #     Logger.info(TAG + "Applying fast flags")
        #     fflags.applyFFlagsToRoblox()

        # launchIntent.setData(Uri.parse(deeplinkUrl))
        Logger.debug(TAG + "Starting intent")
        #currentActivity.startActivity(launchIntent)
        webbrowser.open(deeplinkUrl)
        
        if currentSettings["enableActivityTracking"]:
            Logger.info(TAG + "Starting activity tracker")
            ActivityWatcherSession().start()
else:
    Logger.info(TAG + f"Running on {platform}, not importing.")