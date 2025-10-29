from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
#from kivy.uix.codeinput import CodeInput

from kivymd.app import MDApp
from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle
)
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDIcon, MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from backend.threadtools import scheduleInClock

from typing import Any, Callable, List
import webbrowser

__all__ = [
    "BasicScreen", "FixMDLabel", "SectionText", "IconWithTextDetails",
    "ExtendedButton", "ExtendedToggle", "ExtendedTextField", "DropdownItem",
    "ExtendedDropdown", "NavigationDrawerItem"
]
class BasicScreen(MDScreen):
    name = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.main = MDBoxLayout(
            *args,
            padding = dp(15),
            spacing = dp(15),
            orientation = "vertical",
            adaptive_height = True
        )
        self.add_widget(MDBoxLayout(
            MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon = "menu",
                        on_release = self._toggleDrawer
                    )
                ),
                MDTopAppBarTitle(
                    text = self.name
                )
            ),
            MDScrollView(
                self.main,
                do_scroll_x = False,
                id = "ScrollView"
            ),
            orientation = "vertical"
        ))
        self.md_bg_color = self.theme_cls.backgroundColor

    def _toggleDrawer(self, *args):
        self.parent.parent.get_ids().NavigationDrawer.set_state("open")
    
    def add_widgets(self, *args): # any way to do this efficiently?
        for element in args:
            self.main.add_widget(element)
        print("E", self.get_ids().ScrollView.get_ids())
    def createRef(self, url, text = "Learn more. "):
        primaryColor = self.theme_cls.primaryColor
        r = round(primaryColor[0] * 255)
        g = round(primaryColor[1] * 255)
        b = round(primaryColor[2] * 255)
        hex = f"#{r:02X}{g:02X}{b:02X}"
        return f"[ref={url}][color={hex}][u]{text}[/u][/color][/ref]"

class FixMDLabel(MDLabel):
    fontSize = NumericProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_size = self.fontSize

class SectionText(MDLabel):
    def __init__(self, text, *args, **kwargs):
        super().__init__(
            text = text, 
            bold = True, 
            font_style = "Label",
            adaptive_height = True,
            *args, **kwargs
        )
        self.text_color = self.theme_cls.primaryColor

# lmao wtf should I call it
class IconWithTextDetails(MDBoxLayout): # inspired by kizzy lol
    icon = StringProperty()
    title = StringProperty()
    subtitle = StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ripple_behavior = True
        self.spacing = dp(15)
        self.size_hint = (1, None)
        self.adaptive_height = True

        if self.icon:
            iconToSet = MDIcon(
                icon = self.icon,
                icon_color = self.theme_cls.primaryColor,
                pos_hint = {"center_y": 0.5 }
            )
            iconToSet.font_size = dp(25)
            self.add_widget(iconToSet)
        
        self.mainTitle = FixMDLabel(
            text = self.title,
            font_style = "Title",
            fontSize = dp(19),
            adaptive_height = True
        )
        self.mainSubtitle = MDLabel(
            text = self.subtitle,
            markup = True,
            on_ref_press = lambda instance, url: webbrowser.open(url),
            font_style = "Label",
            role = "medium",
            adaptive_height = True
        )
        self.add_widget(
            MDBoxLayout(
                self.mainTitle, self.mainSubtitle,
                pos_hint = {"center_y": 0.5},
                adaptive_height = True,
                spacing = -5,
                orientation = "vertical",
            )
        )

class ExtendedButton(RectangularRippleBehavior, IconWithTextDetails):
    callback = ObjectProperty(lambda x: ...)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def start_ripple(self): # TODO: improve this
        scheduleInClock(self.callback)(self)
        super().start_ripple()
    

class ExtendedToggle(IconWithTextDetails):
    callback: Callable[[bool], None] = ObjectProperty(lambda x: None) # epllipsis doesnt work?
    active = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = MDSwitch(
            on_release = lambda x: self.callback(not x.active),
            pos_hint = {"center_y": 0.5}
        )
        self.main.active = self.active
        self.add_widget(self.main)

class ExtendedTextField(IconWithTextDetails):
    callback: Callable[[str], None] = ObjectProperty(lambda x: None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = MDTextField(
            mode = "outlined",
            pos_hint = {"center_y": 0.5},
            size_hint_x = 0.2,
            size_hint_y = 1
        )
        self.main.bind(focus=lambda _, focus: (
            self.callback(self.main.text) if not focus else None
        ))
        self.add_widget(self.main)

class DropdownItem:
    def __init__(self, text: str, onRelease: Callable[[str], None] = lambda: ...):
        self.text = text
        self.on_release = onRelease

class ExtendedDropdown(IconWithTextDetails):
    items: List[DropdownItem] = ObjectProperty()
    default: str = StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropItemMenu: MDDropdownMenu = None
        self.dropDownItemText = MDDropDownItemText(text = self.default)
        self.add_widget(
            MDDropDownItem(
                self.dropDownItemText,
                pos_hint = {"center_y": 0.5},
                on_release = self._openMenu
            )
        )
    
    def _openMenu(self, caller):
        if not self.dropItemMenu:
            self.items = [{"text": i.text, "on_release": lambda item=i: self._menuCallback(item.text, item.on_release)} for i in self.items]
            self.dropItemMenu = MDDropdownMenu(
                caller = caller, items = self.items
            )
        self.dropItemMenu.open()
    
    def _menuCallback(self, text: str, originalCallback):
        originalCallback()

        self.dropDownItemText.text = text
        self.dropItemMenu.dismiss()

class NavigationDrawerItem(MDNavigationDrawerItem):
    icon = StringProperty()
    text = StringProperty()
    callback: Callable[[str], None] = ObjectProperty(lambda x: ...)

    def _closeDrawerAndCall(self):
        self.parent.parent.parent.set_state("closed")
        self.callback(self.text)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_release = self._closeDrawerAndCall
        self.add_widget(
            MDNavigationDrawerItemLeadingIcon(
                icon = self.icon
            )
        )
        self.add_widget(
            MDNavigationDrawerItemText(
                text = self.text
            )
        )