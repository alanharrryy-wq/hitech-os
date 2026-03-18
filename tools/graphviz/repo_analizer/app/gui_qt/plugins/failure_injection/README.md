# Failure Injection Plugin

Deterministic plugin used to validate failure paths in the plugin/runtime pipeline.

Control mode with:

```powershell
$env:HITECH_QT_FAILURE_INJECTION_MODE = 'off'         # default, no-op
$env:HITECH_QT_FAILURE_INJECTION_MODE = 'load'        # load failure
$env:HITECH_QT_FAILURE_INJECTION_MODE = 'init'        # initialization failure
$env:HITECH_QT_FAILURE_INJECTION_MODE = 'integration' # dock integration failure
```

This plugin is safe by default (`off`) and only injects failures when explicitly enabled.

