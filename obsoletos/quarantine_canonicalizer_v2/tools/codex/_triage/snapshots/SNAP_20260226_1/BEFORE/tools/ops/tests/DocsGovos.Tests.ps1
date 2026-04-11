Set-StrictMode -Version Latest

function Get-RepoRoot {
  $raw = & git rev-parse --show-toplevel 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw ('Unable to resolve repo root: ' + (($raw | ForEach-Object { [string]$_ }) -join '; '))
  }
  return [string](@($raw | ForEach-Object { [string]$_ }) | Select-Object -First 1)
}

function Get-FrontMatterMap {
  param([string]$Text)

  $out = @{}
  $lines = @($Text -split "`r?`n")
  if ($lines.Count -lt 3) {
    return $out
  }
  if ($lines[0].Trim() -ne '---') {
    return $out
  }

  $end = -1
  for ($i = 1; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq '---') {
      $end = $i
      break
    }
  }
  if ($end -lt 1) {
    return $out
  }

  for ($i = 1; $i -lt $end; $i++) {
    if ($lines[$i] -match '^([A-Za-z0-9_]+):\s*(.*)$') {
      $out[$matches[1].ToLowerInvariant()] = $matches[2].Trim()
    }
  }
  return $out
}

Describe 'GOVOS canonical governance docs' {
  $repoRoot = Get-RepoRoot
  $govRoot = Join-Path $repoRoot 'docs/govos'

  It 'MANIFEST exists' {
    Test-Path -LiteralPath (Join-Path $govRoot 'MANIFEST.yaml') -PathType Leaf | Should Be $true
  }

  It 'canonical governance docs are present' {
    $required = @(
      'docs/govos/README.md',
      'docs/govos/MASTER_INDEX.md',
      'docs/govos/u1_constitutional_change/U1_CONSTITUTIONAL_CHANGE.md',
      'docs/govos/u2_evidence_chain/U2_EVIDENCE_CHAIN.md',
      'docs/govos/u3_policy_plane/U3_POLICY_PLANE.md',
      'docs/govos/u4_enterprise_agents/U4_ENTERPRISE_AGENTS.md'
    )
    foreach ($rel in $required) {
      $path = Join-Path $repoRoot ($rel -replace '/', '\')
      (Test-Path -LiteralPath $path -PathType Leaf) | Should Be $true
    }
  }

  It 'has no duplicate doc_id in docs/govos' {
    $docs = Get-ChildItem -Path $govRoot -Recurse -File -Filter '*.md' | Where-Object {
      $_.FullName -notmatch '\\docs\\govos\\_reports\\'
    }
    $docIds = @{}
    foreach ($doc in $docs) {
      $text = Get-Content -LiteralPath $doc.FullName -Raw -Encoding UTF8
      $fm = Get-FrontMatterMap -Text $text
      if ($fm.ContainsKey('doc_id') -and -not [string]::IsNullOrWhiteSpace($fm['doc_id'])) {
        $id = $fm['doc_id']
        if (-not $docIds.ContainsKey($id)) {
          $docIds[$id] = @()
        }
        $docIds[$id] += $doc.FullName
      }
    }

    $dups = @($docIds.GetEnumerator() | Where-Object { @($_.Value).Count -gt 1 })
    @($dups).Count | Should Be 0
  }

  It 'manifest artifact paths are sorted deterministically' {
    $manifestPath = Join-Path $govRoot 'MANIFEST.yaml'
    $text = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8
    $paths = @()
    foreach ($line in @($text -split "`r?`n")) {
      if ($line -match '^\s*-\s+path:\s*(.+)\s*$') {
        $paths += $matches[1].Trim().Trim('"', "'")
      }
    }
    $sorted = @($paths | Sort-Object)
    ($paths -join '|') | Should Be ($sorted -join '|')
  }

  It 'canonical docs have valid front matter' {
    $docs = Get-ChildItem -Path $govRoot -Recurse -File -Filter '*.md' | Where-Object {
      $_.FullName -notmatch '\\docs\\govos\\_reports\\'
    }

    foreach ($doc in $docs) {
      $text = Get-Content -LiteralPath $doc.FullName -Raw -Encoding UTF8
      $lines = @($text -split "`r?`n")
      ($lines.Count -ge 3) | Should Be $true
      ($lines[0].Trim() -eq '---') | Should Be $true
      (@($lines | Where-Object { $_.Trim() -eq '---' }).Count -ge 2) | Should Be $true

      $fm = Get-FrontMatterMap -Text $text
      $fm.ContainsKey('doc_id') | Should Be $true
      $fm.ContainsKey('title') | Should Be $true
      $fm.ContainsKey('doc_type') | Should Be $true
    }
  }
}
