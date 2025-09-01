package com.drake;

import com.drake.WCCCallback;

import android.webkit.WebView;
import android.webkit.WebChromeClient;
import android.webkit.JsResult;

import java.lang.String;

public class CustomWCC extends WebChromeClient {
    public WCCCallback callback_wrapper;

    public CustomWCC(WCCCallback callback_wrapper) {
	    this.callback_wrapper = callback_wrapper;
    }
    
    @Override
    public boolean onJsAlert(WebView webview, String url, String message, JsResult result) {
        this.callback_wrapper.onJsAlert(message);
        return true;
    }

}