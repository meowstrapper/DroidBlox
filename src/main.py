from kivy.logger import Logger, LOG_LEVELS

import logging

TAG = "DBMain" + ": "

Logger.setLevel(LOG_LEVELS["debug"]) # keep this as builds will be in debug first
logging.getLogger("kivy.jnius").setLevel(logging.INFO)

from frontend.gui import DroidBloxGUI
Logger.info(TAG + "Loading GUI")
DroidBloxGUI().run()