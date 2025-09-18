# TODO: Remove this in the future because you can just launch roblox by opening roblox://

from kivy.logger import Logger
from kivy.utils import platform

TAG = "DBLaunchRoblox" + ": "

__all__ = ["launchRoblox"]

if platform == "android":
    from android import mActivity # type: ignore
    from jnius import autoclass, cast
    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")

    def launchRoblox(deeplinkUrl = "roblox://"):
        Logger.info(TAG + f"Launching roblox with deeplink url: {deeplinkUrl}")
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setData(Uri.parse(deeplinkUrl))
        currentActivity = cast('android.app.Activity', mActivity)
        Logger.debug(TAG + "Starting intent")
        currentActivity.startActivity(intent)
else:
    Logger.info(TAG + f"Running on {platform}, not importing.")