#Requires AutoHotkey v2.0
#SingleInstance Force

global LOG_FILE := A_ScriptDir "\AHK_SMOKE_TEST.log"
global STEP_SEQ := 0

ResetLog()

try {
    Main()
} catch Error as err {
    FailExit("Unhandled error: " err.Message)
}

Main() {
    local targetFolder := A_ScriptDir "\..\HITECHOS__A_core"
    local codeHwnd := 0
    local smokeMessage := "SMOKE TEST: If you can read this, respond with OK."
    local workerTitleFragment := "HITECHOS__A_core"

    if !DirExist(targetFolder) {
        FailExit("Step 1 failed: Worker folder not found: " targetFolder)
    }

    LogStep("Step 1: Opening one VS Code window.")
    if !LaunchVSCode(targetFolder) {
        FailExit("Step 1 failed: Could not launch VS Code.")
    }

    codeHwnd := WaitForWorkerWindow(workerTitleFragment, 20000)
    if !codeHwnd {
        LogStep("Worker title not detected, falling back to active VS Code window.")
        codeHwnd := WaitForAnyCodeWindow(10000)
    }

    if !codeHwnd {
        FailExit("Step 1 failed: Timed out waiting for any VS Code window.")
    }

    LogStep("Step 2: Activating VS Code window.")
    if !ActivateWindow(codeHwnd, 10000) {
        FailExit("Step 2 failed: Could not activate VS Code window.")
    }

    LogStep("Step 3: Pressing Ctrl+Shift+P.")
    EnsureActiveOrFail(codeHwnd, "Step 3 failed: VS Code window is not active.")
    SendKeysOrFail("^+p", "Step 3 failed: Unable to send Ctrl+Shift+P.")
    Sleep(300)

    LogStep("Step 4: Typing command text exactly.")
    EnsureActiveOrFail(codeHwnd, "Step 4 failed: VS Code window is not active.")
    SendTextOrFail("Open Codex Sidebar", "Step 4 failed: Unable to type command text.")
    Sleep(300)

    LogStep("Step 5: Pressing Enter to run command.")
    EnsureActiveOrFail(codeHwnd, "Step 5 failed: VS Code window is not active.")
    SendKeysOrFail("{Enter}", "Step 5 failed: Unable to press Enter.")
    Sleep(400)

    LogStep("Step 6: Waiting 40 seconds.")
    Sleep(40000)

    LogStep("Step 7: Typing smoke-test message.")
    EnsureActiveOrFail(codeHwnd, "Step 7 failed: VS Code window is not active.")
    SendTextOrFail(smokeMessage, "Step 7 failed: Unable to type smoke-test message.")
    Sleep(200)

    LogStep("Step 8: Submitting with exactly one Enter.")
    EnsureActiveOrFail(codeHwnd, "Step 8 failed: VS Code window is not active.")
    ; Exactly one submit keypress: single Enter, no Ctrl+Enter, no retries.
    SendKeysOrFail("{Enter}", "Step 8 failed: Unable to press single Enter.")

    LogStep("Step 9: Stop.")
    ExitApp(0)
}

LaunchVSCode(folder) {
    local q := Chr(34)

    try {
        Run("code --new-window " q folder q)
        return true
    } catch Error as err1 {
        local localAppData := EnvGet("LOCALAPPDATA")
        if !localAppData {
            LogStep("LOCALAPPDATA is not available.")
            return false
        }

        local codeExe := localAppData "\Programs\Microsoft VS Code\Code.exe"
        if !FileExist(codeExe) {
            LogStep("Launch failed via PATH and fallback exe missing: " err1.Message)
            return false
        }

        try {
            Run(q codeExe q " --new-window " q folder q)
            return true
        } catch Error as err2 {
            LogStep("Launch failed via fallback exe: " err2.Message)
            return false
        }
    }
}

WaitForWorkerWindow(titleFragment, timeoutMs) {
    local deadline := A_TickCount + timeoutMs

    while (A_TickCount < deadline) {
        local hwnd := WinExist(titleFragment " ahk_exe Code.exe")
        if hwnd {
            return hwnd
        }
        Sleep(200)
    }

    return 0
}

WaitForAnyCodeWindow(timeoutMs) {
    local deadline := A_TickCount + timeoutMs

    while (A_TickCount < deadline) {
        local activeHwnd := WinActive("ahk_exe Code.exe")
        if activeHwnd {
            return activeHwnd
        }

        local windows := WinGetList("ahk_exe Code.exe")
        if windows.Length > 0 {
            return windows[1]
        }

        Sleep(200)
    }

    return 0
}

ActivateWindow(hwnd, timeoutMs) {
    try {
        WinActivate("ahk_id " hwnd)
    } catch {
        return false
    }

    local deadline := A_TickCount + timeoutMs
    while (A_TickCount < deadline) {
        if WinActive("ahk_id " hwnd) {
            return true
        }
        Sleep(100)
    }

    return false
}

EnsureActiveOrFail(hwnd, failMessage) {
    if WinActive("ahk_id " hwnd) {
        return
    }

    if !ActivateWindow(hwnd, 5000) {
        FailExit(failMessage)
    }
}

SendKeysOrFail(keys, failMessage) {
    try {
        Send(keys)
    } catch Error as err {
        FailExit(failMessage " " err.Message)
    }
}

SendTextOrFail(text, failMessage) {
    try {
        SendText(text)
    } catch Error as err {
        FailExit(failMessage " " err.Message)
    }
}

ResetLog() {
    global LOG_FILE, STEP_SEQ
    STEP_SEQ := 0
    try {
        FileDelete(LOG_FILE)
    } catch {
    }
}

LogStep(message) {
    global LOG_FILE, STEP_SEQ
    STEP_SEQ += 1
    local stamp := FormatTime(, "yyyy-MM-dd HH:mm:ss")
    try {
        FileAppend(Format("{:03d} | {} | {}`r`n", STEP_SEQ, stamp, message), LOG_FILE, "UTF-8")
    } catch {
    }
}

FailExit(message, exitCode := 1) {
    LogStep("FAIL: " message)
    ExitApp(exitCode)
}
