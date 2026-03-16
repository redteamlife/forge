# forge-sync-public.ps1 — Import an accepted public PR into the private dev repo.
#
# Usage:
#   .\scripts\forge-sync-public.ps1 -Pr <number> [-DryRun]
#   .\scripts\forge-sync-public.ps1 -MergeCommit <sha> [-Pr <number>] [-DryRun]

param(
  [string]$Pr = "",
  [string]$MergeCommit = "",
  [switch]$DryRun = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-Command([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    Write-Error "'$cmd' is required but not found in PATH."
    exit 1
  }
}

function Get-YamlValue([string]$FilePath, [string]$Key) {
  $lines = Get-Content $FilePath
  foreach ($line in $lines) {
    if ($line -match "^${Key}:\s*(.+)$") {
      return $Matches[1].Trim().Trim('"').Trim("'")
    }
  }
  return ""
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

function Add-TaskStub([string]$TasksFile, [string]$TaskId, [string]$Description) {
  if (-not (Test-Path $TasksFile)) {
    Write-Host "NOTE: $TasksFile not found. Skipping task stub creation."
    return
  }
  $content = Get-Content $TasksFile -Raw
  if ($content -match "id:\s+$([regex]::Escape($TaskId))") {
    Write-Host "NOTE: Task '$TaskId' already exists in $TasksFile."
    return
  }
  Add-Content -Path $TasksFile -Value ""
  Add-Content -Path $TasksFile -Value "  - id: $TaskId"
  Add-Content -Path $TasksFile -Value "    description: $Description"
  Add-Content -Path $TasksFile -Value "    status: incomplete"
  Write-Host "Added intake task stub to $TasksFile"
}

if ([string]::IsNullOrWhiteSpace($Pr) -and [string]::IsNullOrWhiteSpace($MergeCommit)) {
  Write-Error "Pass -Pr <number> or -MergeCommit <sha>."
  exit 1
}

Require-Command "git"

$forgeYaml = Join-Path (Get-Location) "forge.yaml"
if (-not (Test-Path $forgeYaml)) {
  Write-Error "forge.yaml not found in the current directory."
  exit 1
}

$visibility = Get-YamlValue $forgeYaml "visibility"
$srcDir = Get-YamlValue $forgeYaml "src_dir"
$publicRepo = Get-YamlNested $forgeYaml "repos" "public"
if ($visibility -ne "open-source") {
  Write-Error "forge-sync-public is only valid for open-source tools."
  exit 1
}

$remotes = git remote
if ($remotes -notcontains "public") {
  Write-Error "git remote 'public' is not configured."
  exit 1
}

$status = git status --short 2>&1
if ($status) {
  Write-Error "Working tree is not clean. Commit or stash changes before importing a public PR."
  exit 1
}

$publicUrl = git remote get-url public
$publicRepoFull = $publicRepo
if ($publicRepoFull -notmatch "/") {
  $publicRepoFull = ($publicUrl -replace '^(git@[^:]+:|https?://[^/]+/)', '') -replace '\.git$', ''
}

if (-not [string]::IsNullOrWhiteSpace($Pr)) {
  Require-Command "gh"
  $mergedAt = gh api "repos/$publicRepoFull/pulls/$Pr" --jq ".merged_at"
  if ([string]::IsNullOrWhiteSpace($mergedAt) -or $mergedAt -eq "null") {
    Write-Error "PR #$Pr is not merged in $publicRepoFull."
    exit 1
  }
  $MergeCommit = gh api "repos/$publicRepoFull/pulls/$Pr" --jq ".merge_commit_sha"
}

if ([string]::IsNullOrWhiteSpace($MergeCommit)) {
  Write-Error "Could not resolve merge commit."
  exit 1
}

$taskId = "intake-public-commit-$($MergeCommit.Substring(0,7))"
$taskDesc = "Review, validate, and integrate accepted public commit $($MergeCommit.Substring(0,7)) from $publicRepoFull into the private dev workflow."
if (-not [string]::IsNullOrWhiteSpace($Pr)) {
  $taskId = "intake-public-pr-$Pr"
  $taskDesc = "Review, validate, and integrate accepted public PR #$Pr from $publicRepoFull into the private dev workflow."
}

Write-Host "Fetching public remote..."
git fetch public | Out-Null

$parents = git show --no-patch --format=%P $MergeCommit
$parentCount = ($parents -split '\s+' | Where-Object { $_ }).Count
$patchFile = [System.IO.Path]::GetTempFileName()

if ($DryRun) {
  Write-Host "[dry-run] Would import $MergeCommit from $publicRepoFull into $(git branch --show-current)"
  Write-Host "[dry-run] Would map public repo paths into $srcDir/"
  Write-Host "[dry-run] Would append task stub '$taskId' to docs/forge/TASKS.yaml if missing"
  exit 0
}

try {
  if ($parentCount -gt 1) {
    git diff "$MergeCommit^1" $MergeCommit | Out-File -FilePath $patchFile -Encoding utf8
  } else {
    git diff "$MergeCommit^" $MergeCommit | Out-File -FilePath $patchFile -Encoding utf8
  }

  $patch = Get-Content $patchFile -Raw
  $patch = $patch -replace ' a/', " a/$($srcDir.TrimEnd('/','\'))/"
  $patch = $patch -replace ' b/', " b/$($srcDir.TrimEnd('/','\'))/"
  Set-Content -Path $patchFile -Value $patch -Encoding utf8

  git apply --index $patchFile
} finally {
  Remove-Item -Force $patchFile -ErrorAction SilentlyContinue
}

Add-TaskStub (Join-Path (Get-Location) "docs/forge/TASKS.yaml") $taskId $taskDesc

Write-Host ""
Write-Host "Imported public change into the working tree without committing."
Write-Host "Next steps:"
Write-Host "  1. Review and test the imported change."
Write-Host "  2. Complete the intake task '$taskId' in docs/forge/TASKS.yaml."
Write-Host "  3. Commit it under normal FORGE governance."
