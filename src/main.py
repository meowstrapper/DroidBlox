from kivy.logger import Logger, LOG_LEVELS
from frontend.gui import DroidBloxGUI

import logging

TAG = "DBMain" + ": "

Logger.setLevel(LOG_LEVELS["debug"]) # keep this as builds will be in debug first
logging.getLogger("kivy.jnius").setLevel(logging.INFO)

Logger.info(TAG + "Loading GUI")
DroidBloxGUI().run()