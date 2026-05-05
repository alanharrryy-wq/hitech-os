# Tooling Scripts

Repository operational scripts belong here.

Current launcher entrypoint remains at:
`F:\repos\hitech-os\apps\terminal-de-venta-system\terminal_de_venta.cmd`

ChatGPT share surface maintenance:
`python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share.py --sync`

Freshness status:
`python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share.py --status`

Auto-refresh task install:
`python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share.py --install-scheduled-task`

Auto-refresh task status:
`python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share.py --task-status`

Auto-refresh task uninstall:
`python F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share.py --uninstall-scheduled-task`

Scheduled execution uses the hidden launcher:
`F:\repos\hitech-os\apps\terminal-de-venta-system\tooling\scripts\sync_chatgpt_share_hidden.vbs`

The hidden launcher uses `pythonw.exe` and `--background` so scheduled refresh does not spawn console windows.
