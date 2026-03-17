Param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [String[]]$ArgList
)

python tools/codex/factory_cli.py @ArgList
exit $LASTEXITCODE
