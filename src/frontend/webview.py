"""
Credits:
https://github.com/arncode90/kivy-custom-webview
https://github.com/dead8309/Kizzy
"""
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.utils import platform

TAG = "DBWebview" + ": "

if platform == "android":
    from android import mActivity # type: ignore
    from android.runnable import run_on_ui_thread # type: ignore
    from jnius import autoclass, PythonJavaClass, java_method
    
    Logger.debug(TAG + "Importing classes")
    Build = autoclass("android.os.Build")

    WebView = autoclass("android.webkit.WebView")
    WebViewClient = autoclass("com.drake.CustomWVC")    
    WebChromeClient = autoclass("com.drake.CustomWCC")

    View = autoclass('android.view.View')
    viewGroup = autoclass('android.view.ViewGroup')
    layoutParams = autoclass('android.view.ViewGroup$LayoutParams')
    Logger.debug(TAG + "Done importing classes")

    DISCORD_LOGIN_URL = "https://discord.com/login"
    JS_SNIPPET = "javascript:(function()%7Bvar%20i%3Ddocument.createElement('iframe')%3Bdocument.body.appendChild(i)%3Balert(i.contentWindow.localStorage.token.slice(1,-1))%7D)()"
    MOTOROLA = "motorola"
    SAMSUNG_USER_AGENT = "Mozilla/5.0 (Linux; Android 14; SM-S921U; Build/UP1A.231005.007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.363"

    class WVCCallback(PythonJavaClass):
        __javacontext__ = "app"
        __javainterfaces__ = ["com/drake/WVCCallback"]

        def __init__(self, callback):
            super().__init__()
            self.callback = callback
        
        @java_method("(Ljava/lang/String;)Z")
        def shouldOverrideUrlLoading(self, url):
            self.callback(url)

    class WCCCallback(PythonJavaClass):
        __javacontext__ = "app"
        __javainterfaces__ = ["com/drake/WCCCallback"]

        def __init__(self, callback):
            super().__init__()
            self.callback = callback
        
        @java_method("(Ljava/lang/String;)Z")
        def onJsAlert(self, message):
            self.callback(message)
    
    class WebViewWindow:
        def __init__(self, url, **kwargs):
            self.url = url
            # self.x = x
            # self.y = y
            # self.width = width
            # self.height = height

        def shouldOverrideUrlLoading(self, url): ...
        def onJsAlert(self, message): ... 

        @run_on_ui_thread
        def webviewSetup(self):
            Logger.debug(TAG + "Creating webview")
            self.webview = WebView(mActivity)

            self.wvcCallback = WVCCallback(self.shouldOverrideUrlLoading)
            self.webViewClient = WebViewClient(self.wvcCallback)
            self.webview.setWebViewClient(self.webViewClient)

            self.wccCallback = WCCCallback(self.onJsAlert)
            self.webChromeClient = WebChromeClient(self.wccCallback)
            self.webview.setWebChromeClient(self.webChromeClient)

            Logger.debug(TAG + "Setting settings")
            settings = self.webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            
            if Build.MANUFACTURER.lower() == MOTOROLA:
                Logger.info(TAG + "Device is a motorola, changing user agent to samsung.")
                settings.setUserAgentString(SAMSUNG_USER_AGENT)

            Logger.debug(TAG + "Done, adding content view to activity and setting it to visible")
            mActivity.addContentView(self.webview, layoutParams(Window.width, Window.height))
            self.webview.setVisibility(View.VISIBLE)
        
        @run_on_ui_thread
        def startWebview(self):
            Logger.info(TAG + "Starting webview")
            self.webviewSetup()
            self.webview.loadUrl(self.url)
        
        @run_on_ui_thread
        def closeWebview(self):
            Logger.info(TAG + "Closing webview")
            self.webview.stopLoading()
            self.webview.setVisibility(View.GONE)
            self.webview.destroy()
    
    class DiscordLoginWebView(WebViewWindow):
        def __init__(self, **kwargs):
            super().__init__(url = DISCORD_LOGIN_URL, **kwargs)
        
        def onLoginCompleted(self, token: str): ...

        def shouldOverrideUrlLoading(self, url: str):
            if url.endswith("/app"):
                Logger.debug(TAG + f"Redirected to {url}, loading javascript.")
                self.webview.loadUrl(JS_SNIPPET)
            return super().shouldOverrideUrlLoading(url)
        
        def onJsAlert(self, message):
            self.onLoginCompleted(message)
            self.closeWebview()
            return super().onJsAlert(message)
else:
    Logger.info(TAG + f"Running on {platform}, not importing!")