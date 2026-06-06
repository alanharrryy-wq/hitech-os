Set oShell = CreateObject("WScript.Shell")
cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""F:\repos\hitech-os\tools\code-atlas\launcher\Launch-CodeAtlas.ps1"""
oShell.Run cmd, 0, False
