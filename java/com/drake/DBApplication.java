// made by gemini, pls report any bad code here!!! (and how to fix if you can:3)
package com.drake;

import android.app.ActivityManager;
import android.app.Application;
import android.content.Context;
import android.os.Debug;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

public class DBApplication extends Application {

    private static final String TAG = "DBApplication";

    private final Handler handler = new Handler(Looper.getMainLooper());

    private final Runnable memoryLogger = new Runnable() {
        @Override
        public void run() {
            handler.postDelayed(this, 60000);
        }
    };

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "onCreate()");
        handler.post(memoryLogger);
    }

    @Override
    public void onTrimMemory(int level) {
        super.onTrimMemory(level);
        String levelName = getTrimLevelName(level);
        Log.w(TAG, String.format("onTrimMemory() Level: %d (%s)", level, levelName));
        logMemoryUsage("OnTrimMemory Event: " + levelName);
    }

    private void logMemoryUsage(String context) {
        ActivityManager activityManager = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);

        if (activityManager != null) {
            Debug.MemoryInfo[] memoryInfo = activityManager.getProcessMemoryInfo(new int[]{android.os.Process.myPid()});
            
            if (memoryInfo.length > 0) {
                long pssMiB = memoryInfo[0].getTotalPss() / 1024;
                long privateDirtyMiB = memoryInfo[0].getTotalPrivateDirty() / 1024;
                long totalHeap = Runtime.getRuntime().totalMemory() / 1048576;
                long freeHeap = Runtime.getRuntime().freeMemory() / 1048576;
                long usedHeap = totalHeap - freeHeap;

                Log.d(TAG, String.format(
                    "[%s] MEMORY STATS: PSS: %d MiB | Private Dirty: %d MiB | Heap Used: %d MiB / %d MiB (Total)",
                    context,
                    pssMiB,
                    privateDirtyMiB,
                    usedHeap,
                    totalHeap
                ));
            }
        } else {
            Log.e(TAG, "ActivityManager service is not available.");
        }
    }

    private String getTrimLevelName(int level) {
        switch (level) {
            case TRIM_MEMORY_RUNNING_MODERATE:
                return "RUNNING_MODERATE (System moderate pressure)";
            case TRIM_MEMORY_RUNNING_LOW:
                return "RUNNING_LOW (System low on memory)";
            case TRIM_MEMORY_RUNNING_CRITICAL:
                return "RUNNING_CRITICAL (System is critically low)";
            case TRIM_MEMORY_UI_HIDDEN:
                return "UI_HIDDEN (UI not visible, good time to release resources)";
            case TRIM_MEMORY_BACKGROUND:
                return "BACKGROUND (App in background, near end of LRU list)";
            case TRIM_MEMORY_MODERATE:
                return "MODERATE (App in background, system running low)";
            case TRIM_MEMORY_COMPLETE:
                return "COMPLETE (App in background, system needs all resources)";
            default:
                return "UNKNOWN";
        }
    }

    @Override
    public void onTerminate() {
        super.onTerminate();
        // Stop the recurring task when the application process terminates
        handler.removeCallbacks(memoryLogger);
        Log.i(TAG, "onTerminate()");
    }
}
