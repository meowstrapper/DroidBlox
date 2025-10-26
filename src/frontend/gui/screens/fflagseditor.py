from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.codeinput import CodeInput

from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
#from kivymd.toast import toast

from pygments.lexers import JsonLexer

from backend.files import fflags

import json

TAG = "DBFFlagsEditorScreen" + ": "

__all__ = ["FFlagsEditor"]

class FFlagsEditor(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            name = "FastFlagsEditor",
            id = "FastFlagsEditorScreen",
            **kwargs
        )
        self.CodeInput = CodeInput(
            lexer = JsonLexer(),
            auto_indent = True,
            size_hint = (1, 1)
        )
        self.invalidJson = False
        self.CodeInput.bind(focus = lambda a,b: self.checkIfJsonIsValid() if not b else None) # trigger if not focused anymore
        self.JsonStatus = MDLabel(
            text = "JSON is valid.",
            adaptive_height = True
        )
        self.main = MDBoxLayout(
            self.JsonStatus,
            self.CodeInput,
            MDButton(
                MDButtonText(
                    text = "Save"
                ),
                on_press = lambda *args: self.saveFFlags(),
                pos_hint = {"center_x": 0.5}
            ),
            *args,
            padding = dp(15),
            spacing = dp(15),
            orientation = "vertical",
            #adaptive_height = True
        )

        self.add_widget(MDBoxLayout(
            MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon = "arrow-left",
                        on_release = self._goBack
                    )
                ),
                MDTopAppBarTitle(
                    text = "Fast Flag Editor"
                )
            ),
            self.main,
            orientation = "vertical"
        ))
        self.md_bg_color = self.theme_cls.backgroundColor

    def checkIfJsonIsValid(self): # called after codeinput lost focus
        Logger.debug(TAG + "Checking if json is valid..")
        try:
            json.loads(self.CodeInput.text)
            Logger.debug(TAG + "JSON is valid.")
            self.invalidJson = False
            self.JsonStatus.text = "JSON is valid."
        except Exception as e:
            Logger.error(TAG + f"JSON Invalid! {e}")
            self.invalidJson = True
            self.JsonStatus.text = f"JSON Invalid! {e}"
    
    def saveFFlags(self):
        Logger.debug(TAG + "Attempting to save fflags")

        if self.invalidJson:
            Logger.warning(TAG + "JSON isn't valid, not saving.")
            return
        
        Logger.debug(TAG + "Beautifying JSON text")
        self.CodeInput.text = json.dumps(
            json.loads(self.CodeInput.text),
            indent = 4
        )
        
        try:
            fflags.writeToFFlags(self.CodeInput.text)
        except Exception as e:
            Logger.error(TAG + f"Error while trying to save fflags: {e}")
            self.JsonStatus.text = f"Error while trying to save fflags: {e}"
    
    def mergeFFlagsDialog(self):
        ...
    def on_pre_enter(self, *args):
        Logger.debug(TAG + "Entered screen, setting codeinput text to current fflags")
        self.CodeInput.text = fflags.readRawFFlags()

    def _goBack(self, *args):
        Logger.debug(TAG + "Going back to FFlags screen")
        self.parent.parent.get_ids().ScreenManager.current = "FastFlags"