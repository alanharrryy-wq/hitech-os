Option Explicit

Dim shell
Dim fso
Dim scriptDir
Dim syncScript
Dim localAppData
Dim candidates
Dim candidate
Dim pythonExe
Dim command
Dim exitCode

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
syncScript = fso.BuildPath(scriptDir, "sync_chatgpt_share.py")
localAppData = shell.ExpandEnvironmentStrings("%LocalAppData%")

candidates = Array( _
  localAppData & "\Programs\Python\Python313\pythonw.exe", _
  localAppData & "\Programs\Python\Python312\pythonw.exe", _
  localAppData & "\Programs\Python\Python311\pythonw.exe", _
  "pyw.exe", _
  "pythonw.exe" _
)

pythonExe = ""
For Each candidate In candidates
  If InStr(candidate, "\") > 0 Then
    If fso.FileExists(candidate) Then
      pythonExe = candidate
      Exit For
    End If
  Else
    pythonExe = candidate
    Exit For
  End If
Next

If pythonExe = "" Then
  WScript.Quit 1
End If

command = Quote(pythonExe) & " " & Quote(syncScript) & " --refresh-if-stale --quiet --background"
exitCode = shell.Run(command, 0, True)
WScript.Quit exitCode

Function Quote(value)
  Quote = Chr(34) & value & Chr(34)
End Function
