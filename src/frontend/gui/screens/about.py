from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage

from frontend.gui.elements import (
    BasicScreen,
    FixMDLabel
)

import webbrowser

__all__ = ["About"]

class About(BasicScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "About",
            id = "AboutScreen",
            *args, **kwargs
        )
        self.add_widgets(
            MDBoxLayout(
                FitImage(
                    source = "https://github.com/meowstrapper/DroidBlox/blob/main/assets/icon.png?raw=true",
                    fit_mode = "scale-down"
                ),
                size_hint = (1, None),
                height = dp(150)
            ),
            FixMDLabel(
                text = "DroidBlox is a bootstrapper for Roblox's android client that gives you additional features.\n\n" \
                        f"It is a {self.createRef('https://github.com/bloxstraplabs/bloxstrap', 'Bloxstrap')} alternative to android except there are some features that are [b]not currently possible[/b] in the android version.\n\n" +
                        self.createRef("https://github.com/meowstrapper/DroidBlox/blob/main/LICENSE", "License") + "\n" +
                        self.createRef("https://github.com/meowstrapper/DroidBlox", "GitHub Repo") + "\n" +
                        self.createRef("https://discord.gg/kVmH76umHv", "Discord Server") + "\n" +
                        self.createRef("https://github.com/meowstrapper/DroidBlox?tab=readme-ov-file#credits", "Credits") + "\n" +
                        self.createRef("https://github.com/meowstrapper/DroidBlox?tab=readme-ov-file#licenses-libraries-used-and-codes-that-i-refactored-or-used", "Licenses") + "\n",
                on_ref_press = lambda instance, url: webbrowser.open(url),
                markup = True,
                adaptive_height = True,
                fontSize = dp(17),
                halign = "center"
            )
        )