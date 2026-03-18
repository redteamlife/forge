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

function Test-ReleaseDirIgnored([string]$GitIgnorePath, [string]$IgnoreEntry) {
  if (-not (Test-Path $GitIgnorePath)) { return $false }
  $ignoreLines = Get-Content $GitIgnorePath
  return ($ignoreLines -contains $IgnoreEntry -or $ignoreLines -contains "/$IgnoreEntry")
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
$PublishStrategy = Get-YamlValue $ForgeYaml "publish_strategy"
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
if ($Visibility -eq "open-source") {
  if ([string]::IsNullOrWhiteSpace($PublishStrategy)) { $PublishStrategy = "snapshot-force-push" }
  Write-Host "  strategy   : $PublishStrategy"
}
Write-Host "  src_dir    : $SrcDir"
Write-Host "  release_dir: $ReleaseDir"
Write-Host "  public repo: $PublicRepo"

# ---------------------------------------------------------------------------
# Route by visibility
# ---------------------------------------------------------------------------

Require-Command "git"
$RepoRoot = git rev-parse --show-toplevel 2>$null
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
  $RepoRoot = (Get-Location).Path
}

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
  $gitIgnore = Join-Path $RepoRoot ".gitignore"
  $ignoreEntry = "$($ReleaseDir.TrimEnd('/','\'))/"
  if ([string]::IsNullOrWhiteSpace($PublishStrategy)) { $PublishStrategy = "snapshot-force-push" }
  $publicSyncRequired = Get-YamlNested $ForgeYaml "public_sync" "required"
  $lastImportedPublicCommit = (Get-YamlNested $ForgeYaml "public_sync" "last_imported_public_commit").Trim('"')
  if ($PublishStrategy -notin @("snapshot-force-push", "preserve-history")) {
    Write-Error "Unknown publish_strategy '$PublishStrategy'. Must be 'snapshot-force-push' or 'preserve-history'."
    exit 1
  }

  $null = git ls-remote --exit-code public refs/heads/main 2>$null
  if ($PublishStrategy -eq "preserve-history" -and $LASTEXITCODE -eq 0) {
    git fetch public main:refs/remotes/public/main | Out-Null
    $publicHead = git rev-parse public/main
    if ($publicSyncRequired -eq "true" -and $lastImportedPublicCommit -ne $publicHead) {
      $rangeSpec = "public/main"
      if (-not [string]::IsNullOrWhiteSpace($lastImportedPublicCommit)) {
        $null = git cat-file -e "$lastImportedPublicCommit^{commit}" 2>$null
        if ($LASTEXITCODE -ne 0) {
          Write-Error "last_imported_public_commit '$lastImportedPublicCommit' is not present in public/main history."
          exit 1
        }
        git merge-base --is-ancestor $lastImportedPublicCommit public/main
        if ($LASTEXITCODE -ne 0) {
          Write-Error "last_imported_public_commit '$lastImportedPublicCommit' is not present in public/main history."
          exit 1
        }
        $rangeSpec = "$lastImportedPublicCommit..public/main"
      }

      $nonReleaseSubjects = git log --format=%s $rangeSpec | Where-Object { $_ -ne "release: publish $Project" }
      if ($nonReleaseSubjects) {
        Write-Error "public/main contains merged public changes that have not been imported into private dev.`nRun forge-sync-public before publishing again."
        exit 1
      }
    }
  }

  if ($DryRun) {
    if (-not (Test-ReleaseDirIgnored $gitIgnore $ignoreEntry)) {
      Write-Host "[dry-run] WARNING: '$ignoreEntry' is not in .gitignore. A non-dry-run publish will add it automatically."
    }
    Dry "Remove-Item -Recurse -Force $ReleaseDir; New-Item -ItemType Directory $ReleaseDir"
    Dry "Copy-Item -Recurse $SrcDir\* $ReleaseDir"
    Dry "tmpDir = New-TemporaryFile + mkdir"
    if ($PublishStrategy -eq "snapshot-force-push") {
      Dry "Copy-Item -Recurse $ReleaseDir\* tmpDir"
      Dry "cd tmpDir; git init; git add .; git commit -m 'release: publish $Project'"
      Dry "git remote add public $remoteUrl"
      Dry "git push public main --force"
    } else {
      Dry "cd tmpDir; git init; git remote add public $remoteUrl"
      Dry "git fetch public main; git checkout -B main FETCH_HEAD"
      Dry "clear tmpDir working tree and copy $ReleaseDir into it"
      Dry "git add -A; git commit -m 'release: publish $Project'"
      Dry "git push public main"
    }
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

  if (-not (Test-ReleaseDirIgnored $gitIgnore $ignoreEntry)) {
    Write-Host "WARNING: '$ignoreEntry' is not in .gitignore. Adding it now to prevent release artifacts from being committed."
    Add-Content -Path $gitIgnore -Value $ignoreEntry
  }

  # Populate release staging dir using platform-safe paths
  if (Test-Path $ReleaseDir) { Remove-Item -Recurse -Force $ReleaseDir }
  New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
  Get-ChildItem -Path $SrcDir | Copy-Item -Destination $ReleaseDir -Recurse -Force
  $releaseDirAbs = (Resolve-Path $ReleaseDir).Path

  # Resolve FORGE mode from AI.md for commit trailer
  $forgeMode = "Mid"
  $aiMd = Join-Path (Get-Location) "docs" | Join-Path -ChildPath "forge" | Join-Path -ChildPath "AI.md"
  if (Test-Path $aiMd) {
    $modeLine = Select-String -Path $aiMd -Pattern "^FORGE_mode:" | Select-Object -First 1
    if ($modeLine) { $forgeMode = ($modeLine.Line -split ":\s*")[1].Trim() }
  }

  $tmpRelease = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
  $published = $false
  $hadPublishableChanges = $false
  New-Item -ItemType Directory -Path $tmpRelease -Force | Out-Null

  try {
    Push-Location $tmpRelease
    try {
      git init | Out-Null
      git remote add public $remoteUrl

      if ($PublishStrategy -eq "snapshot-force-push") {
        git symbolic-ref HEAD refs/heads/main
        Get-ChildItem -Path $releaseDirAbs | Copy-Item -Destination $tmpRelease -Recurse -Force
      } else {
        $null = git ls-remote --exit-code public refs/heads/main 2>$null
        if ($LASTEXITCODE -eq 0) {
          git fetch public main | Out-Null
          git checkout -B main FETCH_HEAD | Out-Null
        } else {
          git symbolic-ref HEAD refs/heads/main
        }

        Get-ChildItem -Force -Path $tmpRelease | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force
        Get-ChildItem -Path $releaseDirAbs | Copy-Item -Destination $tmpRelease -Recurse -Force
      }

      git add -A
      git diff --cached --quiet
      if ($LASTEXITCODE -eq 0) {
        $hadPublishableChanges = $false
      } else {
        $hadPublishableChanges = $true
        git commit -m "release: publish $Project`n`nFORGE-mode: $forgeMode`nFORGE-task: RELEASE`nFORGE-gate: pass"

        Print-Step "Pushing to public/$PublicRepo main"
        if ($PublishStrategy -eq "snapshot-force-push") {
          git push public main --force
        } else {
          git push public main
        }
        $published = $true
      }
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
  if ($published) {
    Write-Host "Published $Project to public repo: $PublicRepo"
  } elseif (-not $hadPublishableChanges) {
    Write-Host "No publishable changes detected for $PublicRepo."
  }

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
