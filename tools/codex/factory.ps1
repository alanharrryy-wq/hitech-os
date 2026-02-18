Param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [String[]]$Args
)

python tools/codex/factory_cli.py @Args
exit $LASTEXITCODE
