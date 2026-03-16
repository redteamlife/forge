# forge-publish.ps1 — Publish a FORGE-governed tool to its public repository.
#
# Usage:
#   .\scripts\forge-publish.ps1 [-Tag <version>] [-DryRun]
#
# Options:
#   -Tag <version>   Release tag (e.g. v1.0.0). Required for closed-source.
#                    Prompted interactively if not provided.
#   -DryRun          Print what would happen without making changes.
#
# Reads forge.yaml from the project root. Requires git.
# Closed-source releases require the gh CLI.
# Open-source releases require a configured 'public' remote.
#
# Compatible with PowerShell 5.1+ and PowerShell 7+ (pwsh) on Windows, macOS, Linux.

param(
  [string]$Tag    = "",
  [switch]$DryRun = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Print-Step([string]$msg) {
  Write-Host ""
  Write-Host "==> $msg"
}

function Dry([string]$msg) {
  Write-Host "[dry-run] $msg"
}

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Error "'$cmd' is required but not found in PATH."
    exit 1
  }
}

# ---------------------------------------------------------------------------
# Minimal forge.yaml parser
# Reads key: value pairs and list items without requiring external modules.
# ---------------------------------------------------------------------------

function Get-YamlValue([string]$FilePath, [string]$Key) {
  $lines = Get-Content $FilePath
  foreach ($line in $lines) {
    if ($line -match "^${Key}:\s*(.+)$") {
      return $Matches[1].Trim().Trim('"').Trim("'")
    }
  }
  return ""
}

function Get-YamlList([string]$FilePath, [string]$Key) {
  $lines   = Get-Content $FilePath
  $inBlock = $false
  $items   = @()
  foreach ($line in $lines) {
    if ($line -match "^${Key}:") { $inBlock = $true; continue }
    if ($inBlock) {
      if ($line -match "^  - (.+)$") { $items += $Matches[1].Trim() }
      elseif ($line -notmatch "^\s") { break }
    }
  }
  return $items
}

function Get-YamlNested([string]$FilePath, [string]$Parent, [string]$Key) {
  $lines   = Get-Content $FilePath
  $inBlock = $false
  foreach ($line in $lines) {
    if ($line -match "^${Parent}:") { $inBlock = $true; continue }
    if ($inBlock -and $line -match "^  ${Key}:\s*(.+)$") {
      return $Matches[1].Trim().Trim('"').Trim("'")
    }
    if ($inBlock -and $line -notmatch "^\s") { break }
  }
  return ""
}

# ---------------------------------------------------------------------------
# Validate forge.yaml
# ---------------------------------------------------------------------------

$ForgeYaml = Join-Path (Get-Location) "forge.yaml"

if (-not (Test-Path $ForgeYaml)) {
  Write-Error "forge.yaml not found in the current directory.`nRun this script from the project root."
  exit 1
}

Print-Step "Reading forge.yaml"

$Project    = Get-YamlValue  $ForgeYaml "project"
$Visibility = Get-YamlValue  $ForgeYaml "visibility"
$SrcDir     = Get-YamlValue  $ForgeYaml "src_dir"
$ReleaseDir = Get-YamlValue  $ForgeYaml "release_dir"
$PublicRepo = Get-YamlNested $ForgeYaml "repos" "public"

foreach ($field in @{project=$Project; visibility=$Visibility; src_dir=$SrcDir; release_dir=$ReleaseDir; "repos.public"=$PublicRepo}.GetEnumerator()) {
  if ([string]::IsNullOrWhiteSpace($field.Value)) {
    Write-Error "forge.yaml is missing required field: $($field.Key)"
    exit 1
  }
}

Write-Host "  project    : $Project"
Write-Host "  visibility : $Visibility"
Write-Host "  src_dir    : $SrcDir"
Write-Host "  release_dir: $ReleaseDir"
Write-Host "  public repo: $PublicRepo"

# ---------------------------------------------------------------------------
# Route by visibility
# ---------------------------------------------------------------------------

Require-Command "git"

if ($Visibility -eq "open-source") {

  # -------------------------------------------------------------------------
  # Open source: copy src -> release, then push ONLY release content to
  # public/main using a temporary isolated git repository. This ensures no
  # dev-repo files (FORGE docs, architecture, etc.) are ever pushed to the
  # public repo.
  # -------------------------------------------------------------------------

  Print-Step "Open source publish: copying $SrcDir -> $ReleaseDir"

  if (-not (Test-Path $SrcDir)) {
    Write-Error "src_dir '$SrcDir' does not exist."
    exit 1
  }

  # Validate public remote
  $remotes = git remote
  if ($remotes -notcontains "public") {
    Write-Error "git remote 'public' is not configured.`nAdd it with: git remote add public https://github.com/<org>/$PublicRepo.git"
    exit 1
  }

  $remoteUrl = git remote get-url public

  if ($DryRun) {
    Dry "Remove-Item -Recurse -Force $ReleaseDir; New-Item -ItemType Directory $ReleaseDir"
    Dry "Copy-Item -Recurse $SrcDir\* $ReleaseDir"
    Dry "tmpDir = New-TemporaryFile + mkdir; Copy-Item -Recurse $ReleaseDir\* tmpDir"
    Dry "cd tmpDir; git init; git add .; git commit -m 'release: publish $Project'"
    Dry "git remote add public $remoteUrl"
    Dry "git push public main --force"
    Dry "Remove-Item -Recurse -Force tmpDir"
    Write-Host ""
    Write-Host "[dry-run] Open source publish complete — no changes made."
    exit 0
  }

  # Stash uncommitted dev work so src/ is clean
  $dirty = $false
  $gitStatusOutput = git status --porcelain 2>&1
  if ($gitStatusOutput) {
    $dirty = $true
    git stash | Out-Null
  }

  # Populate release staging dir using platform-safe paths
  if (Test-Path $ReleaseDir) { Remove-Item -Recurse -Force $ReleaseDir }
  New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
  Get-ChildItem -Path $SrcDir | Copy-Item -Destination $ReleaseDir -Recurse -Force

  # Resolve FORGE mode from AI.md for commit trailer
  $forgeMode = "Mid"
  $aiMd = Join-Path (Get-Location) "docs" | Join-Path -ChildPath "forge" | Join-Path -ChildPath "AI.md"
  if (Test-Path $aiMd) {
    $modeLine = Select-String -Path $aiMd -Pattern "^FORGE_mode:" | Select-Object -First 1
    if ($modeLine) { $forgeMode = ($modeLine.Line -split ":\s*")[1].Trim() }
  }

  # Build a fresh isolated repo from only the release content and push it.
  # This guarantees nothing from the dev repo leaks into the public repo.
  $tmpRelease = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
  New-Item -ItemType Directory -Path $tmpRelease -Force | Out-Null

  try {
    Get-ChildItem -Path $ReleaseDir | Copy-Item -Destination $tmpRelease -Recurse -Force

    Push-Location $tmpRelease
    try {
      git init | Out-Null
      git symbolic-ref HEAD refs/heads/main
      git add .
      git commit -m "release: publish $Project`n`nFORGE-mode: $forgeMode`nFORGE-task: RELEASE`nFORGE-gate: pass"
      git remote add public $remoteUrl

      Print-Step "Pushing to public/$PublicRepo main"
      git push public main --force
    } finally {
      Pop-Location
    }
  } finally {
    Remove-Item -Recurse -Force $tmpRelease -ErrorAction SilentlyContinue
  }

  if ($dirty) {
    git stash pop 2>&1 | Out-Null
  }

  Write-Host ""
  Write-Host "Published $Project to public repo: $PublicRepo"

} elseif ($Visibility -eq "closed-source") {

  # -------------------------------------------------------------------------
  # Closed source: upload build_output paths as GitHub Release assets.
  # No source or dev files are pushed anywhere.
  # -------------------------------------------------------------------------

  Require-Command "gh"

  $BuildOutput = Get-YamlList $ForgeYaml "build_output"

  if ($BuildOutput.Count -eq 0) {
    Write-Error "No build_output entries found in forge.yaml."
    exit 1
  }

  Print-Step "Verifying build outputs"
  foreach ($bin in $BuildOutput) {
    if (-not (Test-Path $bin)) {
      Write-Error "Binary not found: $bin`nCompile your project before publishing."
      exit 1
    }
    Write-Host "  Found: $bin"
  }

  if ([string]::IsNullOrWhiteSpace($Tag)) {
    $Tag = Read-Host "Release tag (e.g. v1.0.0)"
  }

  if ([string]::IsNullOrWhiteSpace($Tag)) {
    Write-Error "Release tag is required for closed-source publish."
    exit 1
  }

  $repoFullName = $PublicRepo
  try {
    $repoFullName = gh repo view $PublicRepo --json nameWithOwner -q ".nameWithOwner" 2>&1
  } catch { }

  if ($DryRun) {
    Dry "gh release create $Tag --repo $repoFullName --title '$Project $Tag' --notes 'Release $Tag'"
    foreach ($bin in $BuildOutput) {
      Dry "gh release upload $Tag $bin --repo $repoFullName"
    }
    Write-Host ""
    Write-Host "[dry-run] Closed source publish complete — no changes made."
    exit 0
  }

  Print-Step "Creating GitHub Release $Tag on $PublicRepo"

  gh release create $Tag `
    --repo $repoFullName `
    --title "$Project $Tag" `
    --notes "Release $Tag"

  Print-Step "Uploading release assets"
  foreach ($bin in $BuildOutput) {
    gh release upload $Tag $bin --repo $repoFullName
    Write-Host "  Uploaded: $bin"
  }

  Write-Host ""
  Write-Host "Published $Project $Tag to GitHub Releases on $PublicRepo"

} else {
  Write-Error "Unknown visibility '$Visibility' in forge.yaml. Must be 'open-source' or 'closed-source'."
  exit 1
}
