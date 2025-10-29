# credits:
# https://github.com/kivy/plyer/blob/master/plyer/facades/notification.py
# https://github.com/kivy/plyer/blob/master/plyer/platforms/android/notification.py

from kivy.logger import Logger
from kivy.utils import platform

TAG = "DBNotifications"

__all__ = ["notify"]

if platform == "android":
    from jnius import autoclass, cast
    from android import mActivity # type: ignore

    dbActivity = cast("android.app.Activity", mActivity)

    AndroidString = autoclass('java.lang.String')
    Context = autoclass('android.content.Context')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationChannel = autoclass("android.app.NotificationChannel")
    NotificationManager = autoclass('android.app.NotificationManager')
    PendingIntent = autoclass('android.app.PendingIntent')
    Intent = autoclass('android.content.Intent')
    Toast = autoclass('android.widget.Toast')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')

    Logger.debug(TAG + "Getting activity icon")
    packageManager = dbActivity.getPackageManager()
    activityInfo = packageManager.getActivityInfo(activity.getComponentName(), 0)
    if activityInfo.icon == 0:
        activityInfo = packageManager.getApplicationInfo("com.drake.droidblox", 0)
    
    appIcon = activityInfo.icon

    Logger.debug(TAG + "Getting notification service")
    notifService = cast(NotificationManager, dbActivity.getSystemService(
        Context.NOTIFICATION_SERVICE
    ))

    def notify(title: str, subtitle: str):
        Logger.debug(TAG + "Attempting to notify")
        title = AndroidString(title.encode("utf-8"))
        subtitle = AndroidString(subtitle.encode("utf-8"))

        Logger.debug(TAG + "Building notification")
        channel = NotificationChannel("com.drake.droidblox", title, NotificationManager.IMPORTANCE_DEFAULT)
        notifService.createNotificationChannel(channel)

        Logger.debug(TAG + "Constructing notification")
        noti = NotificationBuilder(dbActivity, "com.drake.droidblox")
        noti.setContentTitle(title)
        noti.setContentText(subtitle)
        noti.setTicker(AndroidString(""))

        Logger.debug(TAG + "Setting icons")
        noti.setSmallIcon(appIcon)
        noti.setLargeIcon(BitmapFactory.decodeFile(appIcon))

        Logger.debug(TAG + "Sending out notification")
        notifService.notify(0, noti.build())
else:
    Logger.info(TAG + f"Running on {platform}, not importing.")