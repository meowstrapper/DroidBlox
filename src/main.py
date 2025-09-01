from kivy.logger import Logger, LOG_LEVELS
from frontend.gui import DroidBloxGUI

TAG = "DBMain" + ": "

Logger.setLevel(LOG_LEVELS["debug"]) # keep this as builds will be in debug first

Logger.info(TAG + "Loading GUI")
DroidBloxGUI().run()

# if not suBinaryPath:
#     Logger.error(TAG + f"Su binary not found, prompting device isnt rooted")
#     gui.promptDeviceIsntRooted()
# else:
#     Logger.info(TAG + f"Checking for root access")
#     try:
#         subprocess.check_output([suBinaryPath, "-c", "echo test"]).decode(errors = "ignore")
#     except subprocess.CalledProcessError as e:
#         Logger.error(TAG + f"Subprocess returned: {e}, prompting root access denied")
#         gui.promptRootAccessRequired()

# Logger.info(TAG + f"Checking if roblox is installed")
# try:
#     checkOutput = subprocess.check_output([suBinaryPath, "-c", "if [ -d /data/user/0/com.roblox.client/ ]; then echo test; fi"]).decode(errors = "ignore")
#     if not checkOutput.startswith("test"):
#         raise Exception("Roblox isn't installed")
# except Exception as e:
#     Logger.error(TAG + f"{e}, Roblox isn't installed, prompting roblox not installed")
#     gui.promptRobloxIsntInstalled()

# currentSettings = settings.readSettings()
# if currentSettings["enableActivityTracking"]:
#     Logger.info(TAG + "Waiting for the latest log file..")
