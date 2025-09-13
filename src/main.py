from kivy.logger import Logger, LOG_LEVELS
from frontend.gui import DroidBloxGUI

TAG = "DBMain" + ": "

Logger.setLevel(LOG_LEVELS["debug"]) # keep this as builds will be in debug first

Logger.info(TAG + "Loading GUI")
DroidBloxGUI().run()