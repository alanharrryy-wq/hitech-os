#Requires AutoHotkey v2.0
out := A_ScriptDir "\AHK_PROBE.log"
FileAppend("probe_ok`r`n", out)
ExitApp(0)
