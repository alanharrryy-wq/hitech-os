# PACKAGING_GUIDE

## Goal

Build a clean, portable zip for `external_interaction_template` that represents the intended source release rather than the state of a developer workstation.

## Packaging principles

1. Build from a **staging directory**, never directly from the working tree.
2. Include only what a recipient needs to install, bootstrap, and understand the project.
3. Exclude build output, dependency trees, caches, and local machine state.
4. Treat demo data as a deliberate packaging decision, not an accidental side effect.

## Recommended package shapes

### Option A. Core source zip

Use this as the default premium artifact.

Include:

- source code
- route/app files
- components
- `src/`
- `public/`
- `prisma/schema.prisma`
- seed/bootstrap sources if they are intended to be run by the recipient
- `package.json`
- lockfile if the release process standardizes one
- `README.md`
- release docs such as this guide and the checklist

Exclude:

- `.next/`
- `node_modules/`
- `*.tsbuildinfo`
- local DB files unless intentionally shipping demo state
- caches, logs, editor folders, and OS junk

### Option B. Core zip + visual system zip

Use this if design-system work and core runtime work move at different speeds.

Core zip:

- schema/runtime/services
- API routes
- data model
- install/bootstrap docs

Visual system zip:

- brand assets
- optional visual primitives
- alternate shells or theme wrappers
- screenshots/reference material

This split helps when UI polish is evolving independently from the schema/runtime contract.

### Option C. Core zip + examples pack

Use this if example schemas or demo content should be optional.

Core zip:

- minimal reusable engine
- one safe reference example at most

Examples pack:

- additional example schemas
- demo content
- nonessential assets
- optional seeded/demo DB if intentionally distributed

This keeps the base artifact lean and reduces confusion about what is framework contract versus sample content.

## What should go into staging

A clean staging directory should look roughly like this:

```text
external_interaction_template/
  .env.example
  .gitignore
  README.md
  IMPLEMENTATION_NOTES.md
  RELEASE_CHECKLIST.md
  PACKAGING_GUIDE.md
  CUSTOMIZATION_GUIDE.md
  installer.py
  package.json
  next.config.mjs
  postcss.config.mjs
  tailwind.config.mjs
  tsconfig.json
  next-env.d.ts
  app/
  components/
  public/
  prisma/
  src/
  tests/
  vitest.config.ts
```

The exact list can vary, but staging should reflect product intent, not workstation residue.

## What must stay out of staging

Never let these slip into the shipping zip unless there is a deliberate exception documented in release notes:

```text
.next/
node_modules/
*.tsbuildinfo
coverage/
dist/
out/
.tmp/
.cache/
.DS_Store
Thumbs.db
prisma/*.db
prisma/*.sqlite
prisma/*.sqlite3
```

## Suggested packaging flow

### Step 1. Create a staging folder

Examples:

- `release/staging/external_interaction_template`
- `%TEMP%\external_interaction_template_release_staging`
- another disposable directory outside the repo root

### Step 2. Copy only approved files

Do not clone the whole repo directory and then hope cleanup catches everything.

Preferred approach:

- create the destination folder
- copy approved top-level files
- copy approved directories one by one
- explicitly omit banned artifacts

### Step 3. Validate staging before zipping

Before creating the archive, verify:

- required root markers exist: `package.json`, `app`, `components`, `src`
- no banned artifacts are present
- docs reflect the exact shipped install flow
- DB inclusion/exclusion matches the release decision

### Step 4. Zip the staging root

Zip the **folder containing the project root** so the archive opens cleanly as:

```text
external_interaction_template/
  package.json
  app/
  components/
  src/
  ...
```

That shape keeps the install story predictable and still allows `installer.py` to recover if a wrapper folder is added.

## Example PowerShell packaging flow

```powershell
$ProjectRoot = "F:\path\to\external_interaction_template"
$StageRoot = "F:\path\to\release\staging"
$StageProject = Join-Path $StageRoot "external_interaction_template"
$ZipPath = "F:\path\to\release\external_interaction_template-0.1.0-clean.zip"

Remove-Item $StageRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $StageProject | Out-Null

$TopLevelFiles = @(
  ".env.example",
  ".gitignore",
  "README.md",
  "IMPLEMENTATION_NOTES.md",
  "RELEASE_CHECKLIST.md",
  "PACKAGING_GUIDE.md",
  "CUSTOMIZATION_GUIDE.md",
  "installer.py",
  "package.json",
  "next.config.mjs",
  "postcss.config.mjs",
  "tailwind.config.mjs",
  "tsconfig.json",
  "next-env.d.ts",
  "vitest.config.ts"
)

foreach ($file in $TopLevelFiles) {
  Copy-Item (Join-Path $ProjectRoot $file) -Destination $StageProject -Force
}

$Folders = @("app", "components", "public", "prisma", "src", "tests")
foreach ($folder in $Folders) {
  Copy-Item (Join-Path $ProjectRoot $folder) -Destination $StageProject -Recurse -Force
}

Get-ChildItem -Path $StageProject -Recurse -Force |
  Where-Object {
    $_.FullName -match "\\node_modules\\|\\.next\\" -or
    $_.Name -like "*.tsbuildinfo" -or
    $_.Name -in @("external-interaction.db", ".DS_Store", "Thumbs.db")
  } |
  Remove-Item -Recurse -Force

Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue
Compress-Archive -Path $StageProject -DestinationPath $ZipPath -CompressionLevel Optimal
```

## Example Bash packaging flow

```bash
PROJECT_ROOT="/path/to/external_interaction_template"
STAGE_ROOT="/tmp/external_interaction_template_release_staging"
STAGE_PROJECT="$STAGE_ROOT/external_interaction_template"
ZIP_PATH="/tmp/external_interaction_template-0.1.0-clean.zip"

rm -rf "$STAGE_ROOT"
mkdir -p "$STAGE_PROJECT"

cp "$PROJECT_ROOT"/.env.example "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/.gitignore "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/README.md "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/IMPLEMENTATION_NOTES.md "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/RELEASE_CHECKLIST.md "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/PACKAGING_GUIDE.md "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/CUSTOMIZATION_GUIDE.md "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/installer.py "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/package.json "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/next.config.mjs "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/postcss.config.mjs "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/tailwind.config.mjs "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/tsconfig.json "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/next-env.d.ts "$STAGE_PROJECT"/
cp "$PROJECT_ROOT"/vitest.config.ts "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/app "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/components "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/public "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/prisma "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/src "$STAGE_PROJECT"/
cp -R "$PROJECT_ROOT"/tests "$STAGE_PROJECT"/

find "$STAGE_PROJECT" \( -name node_modules -o -name .next \) -prune -exec rm -rf {} +
find "$STAGE_PROJECT" -name '*.tsbuildinfo' -delete
find "$STAGE_PROJECT" \( -name 'external-interaction.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) -delete
find "$STAGE_PROJECT" \( -name '.DS_Store' -o -name 'Thumbs.db' \) -delete

rm -f "$ZIP_PATH"
(cd "$STAGE_ROOT" && zip -r "$ZIP_PATH" external_interaction_template)
```

## Packaging decision on the demo DB

Choose one and document it clearly:

### Preferred for clean source release

Do **not** include the SQLite DB. Ship schema and seed path only.

### Acceptable for demo-only artifact

Include the DB in a clearly named demo artifact or examples pack, not in the default clean source zip.

## Minimum release standard

A zip should only be considered clean when:

- it installs through `installer.py`
- `install-report.json` shows no contamination warnings
- bootstrap and smoke checks succeed from the installed copy
- the README/install path matches the actual shipped artifact
