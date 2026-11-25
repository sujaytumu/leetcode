package com.sujaytumu.leetcode;

import android.os.Bundle;
import androidx.activity.OnBackPressedCallback;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Back asks the web app first (it steps back one screen, closes a sheet, or goes to the Problems tab); only when
        // it has nothing left to go back to does the app move to the background.
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (getBridge() == null || getBridge().getWebView() == null) {
                    moveTaskToBack(true);
                    return;
                }
                getBridge().getWebView().evaluateJavascript(
                    "(function(){try{return window.__lcBack?window.__lcBack():false}catch(e){return false}})()",
                    value -> { if (!"true".equals(value)) moveTaskToBack(true); });
            }
        });
    }
}
