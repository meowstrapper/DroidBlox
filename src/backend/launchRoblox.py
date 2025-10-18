# TODO: Remove this in the future

from kivy.logger import Logger
from kivy.utils import platform

from backend.files import settings, fflags

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
            Logger.error(TAG + "launchIntent is None! Not starting.")
            return
        
        if currentSettings["applyFFlags"]:
            Logger.info("Applying fast flags")
            fflags.applyFFlagsToRoblox()
            
        launchIntent.setData(Uri.parse(deeplinkUrl))
        Logger.debug(TAG + "Starting intent")
        currentActivity.startActivity(intent)
else:
    Logger.info(TAG + f"Running on {platform}, not importing.")