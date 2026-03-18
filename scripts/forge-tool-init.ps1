# forge-tool-init.ps1 — Scaffold a new FORGE-governed tool development repository.
#
# Usage:
#   .\scripts\forge-tool-init.ps1 [[-ToolName] <string>]
#
# If ToolName is not provided, the script will prompt for it.
# Requires: git. Optional: gh (GitHub CLI) for repo creation.
#
# Compatible with PowerShell 5.1+ and PowerShell 7+ (pwsh) on Windows, macOS, Linux.

param(
  [Parameter(Position = 0)]
  [string]$ToolName = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ForgeScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ForgeRoot      = Split-Path -Parent $ForgeScriptDir
$ForgeTemplates = Join-Path $ForgeRoot "templates"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Print-Step([string]$msg) {
  Write-Host ""
  Write-Host "==> $msg"
}

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Error "'$cmd' is required but not found in PATH."
    exit 1
  }
}

# ---------------------------------------------------------------------------
# Collect inputs
# ---------------------------------------------------------------------------

if ([string]::IsNullOrWhiteSpace($ToolName)) {
  $ToolName = Read-Host "Tool name (no spaces)"
}

if ([string]::IsNullOrWhiteSpace($ToolName)) {
  Write-Error "Tool name is required."
  exit 1
}

Write-Host ""
Write-Host "Select tool type:"
Write-Host "  1) web-tool"
Write-Host "  2) cli-tool"
Write-Host "  3) script"
$typeChoice = Read-Host "Choice [1-3]"

$ToolType = switch ($typeChoice) {
  "1" { "web-tool" }
  "2" { "cli-tool" }
  "3" { "script" }
  default { Write-Error "Invalid choice."; exit 1 }
}

Write-Host ""
Write-Host "Select tool visibility:"
Write-Host "  1) Open source  (source code published to public repo)"
Write-Host "  2) Closed source (compiled binaries published as GitHub Release assets)"
$visChoice = Read-Host "Choice [1-2]"

$Visibility = switch ($visChoice) {
  "1" { "open-source" }
  "2" { "closed-source" }
  default { Write-Error "Invalid choice."; exit 1 }
}

$DevRepo    = "$ToolName-dev"
$PublicRepo = $ToolName
$TargetDir  = Join-Path (Get-Location) $DevRepo

Write-Host ""
Write-Host "Summary:"
Write-Host "  Tool name  : $ToolName"
Write-Host "  Type       : $ToolType"
Write-Host "  Visibility : $Visibility"
Write-Host "  Dev repo   : $DevRepo  (local directory: $TargetDir)"
Write-Host "  Public repo: $PublicRepo"
Write-Host ""

# Guard against overwriting an existing directory
if (Test-Path $TargetDir) {
  Write-Error "Directory '$TargetDir' already exists.`nChoose a different tool name or remove the existing directory first."
  exit 1
}

$confirm = Read-Host "Proceed? [y/N]"

if ($confirm.ToLower() -ne "y") {
  Write-Host "Aborted."
  exit 0
}

# ---------------------------------------------------------------------------
# Create directory structure
# ---------------------------------------------------------------------------

Require-Command "git"

Print-Step "Creating directory structure in $TargetDir"

$dirs = @(
  (Join-Path $TargetDir "src"),
  (Join-Path $TargetDir "docs"),
  (Join-Path $TargetDir "release"),
  (Join-Path $TargetDir "scripts"),
  (Join-Path $TargetDir "templates")
)
if ($Visibility -eq "closed-source") {
  $dirs += (Join-Path $TargetDir "bin")
}

foreach ($d in $dirs) {
  New-Item -ItemType Directory -Path $d -Force | Out-Null
}

# ---------------------------------------------------------------------------
# Copy FORGE templates
# ---------------------------------------------------------------------------

Print-Step "Copying FORGE templates into templates/"

if (-not (Test-Path $ForgeTemplates)) {
  Write-Error "FORGE templates directory not found at $ForgeTemplates"
  exit 1
}

Copy-Item (Join-Path $ForgeTemplates "*") (Join-Path $TargetDir "templates") -Recurse -Force
Write-Host "  Copied: templates/"

# ---------------------------------------------------------------------------
# Generate forge.yaml
# ---------------------------------------------------------------------------

Print-Step "Generating forge.yaml"

$toolNameLower = $ToolName.ToLower()

if ($Visibility -eq "open-source") {
  $forgeYaml = @"
project: $ToolName

type: $ToolType

visibility: open-source
publish_strategy: preserve-history

src_dir: src
release_dir: release

docs_dir: docs/forge

public_sync:
  required: true
  last_imported_public_commit: ""

sync_map:
  .: src/

repos:
  dev: $DevRepo
  public: $PublicRepo
"@
} else {
  $forgeYaml = @"
project: $ToolName

type: $ToolType

visibility: closed-source

src_dir: src
release_dir: release

docs_dir: docs/forge

build_output:
  - bin/$toolNameLower-linux
  - bin/$toolNameLower-macos
  - bin/$toolNameLower-win.exe

repos:
  dev: $DevRepo
  public: $PublicRepo
"@
}

Set-Content -Path (Join-Path $TargetDir "forge.yaml") -Value $forgeYaml -Encoding UTF8
Write-Host "  Created: forge.yaml"

# ---------------------------------------------------------------------------
# Copy publish scripts
# ---------------------------------------------------------------------------

Print-Step "Copying tool workflow scripts"

foreach ($script in @("forge-publish.sh", "forge-publish.ps1", "forge-sync-public.sh", "forge-sync-public.ps1")) {
  $src = Join-Path $ForgeScriptDir $script
  if (Test-Path $src) {
    Copy-Item $src (Join-Path $TargetDir "scripts" | Join-Path -ChildPath $script)
    Write-Host "  Copied: scripts/$script"
  }
}

# ---------------------------------------------------------------------------
# Create README placeholder
# ---------------------------------------------------------------------------

$readme = @"
# $ToolName

<!-- Replace this with a description of your tool. -->

## Development

This project uses [FORGE](https://github.com/redteamlife/forge) for AI-assisted development governance.

All development occurs in this repository. Releases are published to ``$PublicRepo`` via ``./scripts/forge-publish.sh`` or ``.\scripts\forge-publish.ps1``.

For open-source tools, accepted public pull requests can be imported back into this repo with ``./scripts/forge-sync-public.sh`` or ``.\scripts\forge-sync-public.ps1``.

## Next Step

Run your AI assistant against ``templates/GENERATE_PROJECT_DOCS.md`` to generate the real FORGE governance docs into ``docs/forge/``.
"@

Set-Content -Path (Join-Path $TargetDir "README.md") -Value $readme -Encoding UTF8

# ---------------------------------------------------------------------------
# Create .gitignore
# ---------------------------------------------------------------------------

$gitignore = @"
# Release staging directory — populated by forge-publish, not committed
/release/

# Compiled binaries
/bin/

# OS and editor noise
.DS_Store
Thumbs.db
*.swp
"@

Set-Content -Path (Join-Path $TargetDir ".gitignore") -Value $gitignore -Encoding UTF8

# ---------------------------------------------------------------------------
# Initialize git
# ---------------------------------------------------------------------------

Print-Step "Initializing git repository"

Push-Location $TargetDir
try {
  git init | Out-Null
  # Set default branch to main without requiring git 2.28+
  git symbolic-ref HEAD refs/heads/main
  git add .
  $commitMsg = "chore: initial FORGE scaffold for $ToolName`n`nFORGE-mode: Lightweight`nFORGE-task: INIT-001`nFORGE-gate: pass"
  git commit -m $commitMsg
  Write-Host "  Git repository initialized with initial commit."
} finally {
  Pop-Location
}

# ---------------------------------------------------------------------------
# Optional: create GitHub repos
# ---------------------------------------------------------------------------

Write-Host ""
if (Get-Command "gh" -ErrorAction SilentlyContinue) {
  $createGh = Read-Host "Create GitHub repositories with 'gh'? [y/N]"

  if ($createGh.ToLower() -eq "y") {
    Print-Step "Creating GitHub repositories"

    try {
      gh repo create $DevRepo --private 2>&1 | Out-Null
      Write-Host "  Created private repo: $DevRepo"
    } catch {
      Write-Host "  WARN: Could not create $DevRepo (may already exist or insufficient permissions)"
    }

    try {
      gh repo create $PublicRepo --public 2>&1 | Out-Null
      Write-Host "  Created public repo: $PublicRepo"
    } catch {
      Write-Host "  WARN: Could not create $PublicRepo (may already exist or insufficient permissions)"
    }

    try {
      $ghUser = gh api user -q ".login" 2>&1
      if ($ghUser) {
        Push-Location $TargetDir
        git remote add origin  "https://github.com/$ghUser/$DevRepo.git"
        git remote add public  "https://github.com/$ghUser/$PublicRepo.git"
        Pop-Location
        Write-Host "  Remotes configured: origin ($DevRepo), public ($PublicRepo)"
      }
    } catch {
      Write-Host "  WARN: Could not determine GitHub username for remote configuration."
    }
  }
} else {
  Write-Host "NOTE: 'gh' CLI not found. Add GitHub remotes manually:"
  Write-Host "  git remote add origin  https://github.com/<org>/$DevRepo.git"
  Write-Host "  git remote add public  https://github.com/<org>/$PublicRepo.git"
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

$genDocsPath = Join-Path $ForgeTemplates "GENERATE_PROJECT_DOCS.md"

Write-Host ""
Write-Host "================================================================"
Write-Host "  $ToolName scaffold created at: $TargetDir"
Write-Host "================================================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. cd $DevRepo"
Write-Host "  2. Generate FORGE project docs — point your AI at:"
Write-Host "     templates/GENERATE_PROJECT_DOCS.md"
Write-Host "     and tell it to generate docs for your project into docs/forge/."
Write-Host "  3. Review the generated docs/forge/AI.md and docs/forge/TASKS.yaml"
Write-Host "  4. Start a FORGE session"
Write-Host ""
if ($Visibility -eq "closed-source") {
  Write-Host "  When ready to release:"
  Write-Host "  Compile your binaries to the paths in forge.yaml build_output,"
  Write-Host "  then run: .\scripts\forge-publish.ps1 -Tag v0.1.0"
  Write-Host ""
}
