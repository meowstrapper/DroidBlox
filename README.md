# DroidBlox
<div align="center">
<img src="https://github.com/helloplauz10/DroidBlox/raw/main/droidblox/assets/logo.png" height=300>

![MIT License](https://img.shields.io/github/license/helloplauz10/DroidBlox?color=47b520)
![its slow](https://img.shields.io/badge/made%20with-slow%20python-47b520)
[![Discord Server](https://img.shields.io/discord/1394308437201911920?color=47b520)](https://discord.gg/kVmH76umHv)
</div>

----

DroidBlox is a bootstrapper for Roblox's android client that gives you additional features.

It is a [Bloxstrap](https://github.com/bloxstraplabs/bloxstrap) alternative to android except there are some features that are **not currently possible** in the android version. 

# When will it release?
Anytime soon, maybe if I dont procasinate about making it.

# WARNING!
It's unsure if you will get banned on Roblox for using this, if you have been banned, join [our Discord server](https://discord.gg/zFspvBwH92) and send the ban screenshot there.

The discord rich presence feature uses the Discord gateway connection. **Use it at your own risk.**

# Features
- **Integrations**
    - Launch other intents while launching Roblox (coming soon)
- **Activity Tracking**
    - Notifies you about your current server's location
    - Be able to set your RPC about your playing status (with [BloxstrapRPC](https://github.com/bloxstraplabs/bloxstrap/wiki/Integrating-Bloxstrap-functionality-into-your-game) supported) 
    - Choose if you want others to join you by looking at your RPC
    - Be able to rejoin the last game at the same server you joined
- **Fast Flags**
    - Be able to customize them with ease
    - Merge your current fast flags with other ones
    - Retain your fast flags after updating

# But where's texture configuration?
Roblox recently loaded their assets inside the APK and I cannot find a way to modify the assets **without configuring the APK** which was possible before.

# TODO List
- [ ] Figure out how to set assets
- [x] Make the UX Design with KivyMD
- [ ] Optimize things

# WHY IS IT PYTHON!1!! ITS SO SLOW YK???
I only know python, ehh.. Feel free to recreate my project in Kotlin, Java, or other languages with credits by linking this github repository at yours.

# License
- DroidBlox is licensed under the [GNU GPL v2.0 License](https://github.com/meowstrapper/DroidBlox/blob/main/LICENSE)
- Bloxstrap is license under the [MIT License](https://github.com/bloxstraplabs/bloxstrap/blob/main/LICENSE)

# Credits
- [Julia](https://github.com/juliaoverflow) for allowing me to use her server list of IPs
- [yzziK](https://github.com/dead8309) for allowing me to refactor his code about how [Kizzy](https://github.com/dead8309/Kizzy) connects to Discord gateway and how it also handles the connection
- [Bloxstrap](https://github.com/bloxstraplabs/bloxstrap/) for the functions & classes refactored in python

# Licenses (Libraries used and codes that I refactored or used)
- [Bloxstrap](https://github.com/bloxstraplabs/bloxstrap/blob/main/LICENSE) MIT License
- [KivyMD](https://github.com/kivymd/KivyMD/blob/master/LICENSE) MIT License
- [Kizzy](https://github.com/dead8309/Kizzy/blob/master/License) GNU General Public License v3.0
- [websockets](https://github.com/python-websockets/websockets/blob/main/LICENSE) BSD 3-Clause "New" or "Revised" License
- [pyjnius](https://github.com/kivy/pyjnius/blob/master/LICENSE) MIT License
- [buildozer](https://github.com/kivy/buildozer/blob/master/LICENSE) MIT License
