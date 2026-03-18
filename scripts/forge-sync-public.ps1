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

function Get-YamlBlockMap([string]$FilePath, [string]$Parent) {
  $map = @{}
  $lines = Get-Content $FilePath
  $inBlock = $false
  foreach ($line in $lines) {
    if ($line -match "^${Parent}:") { $inBlock = $true; continue }
    if ($inBlock -and $line -match "^  ([^:]+):\s*(.+)$") {
      $map[$Matches[1].Trim().Trim('"').Trim("'")] = $Matches[2].Trim().Trim('"').Trim("'")
      continue
    }
    if ($inBlock -and $line -notmatch "^\s") { break }
  }
  return $map
}

function Set-LastImportedCommit([string]$ForgeYamlPath, [string]$Sha) {
  $lines = Get-Content $ForgeYamlPath
  $updated = $false
  for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^  last_imported_public_commit:') {
      $lines[$i] = "  last_imported_public_commit: `"$Sha`""
      $updated = $true
    }
  }
  if (-not $updated) {
    $lines += ""
    $lines += "public_sync:"
    $lines += "  required: true"
    $lines += "  last_imported_public_commit: `"$Sha`""
  }
  Set-Content -Path $ForgeYamlPath -Value $lines -Encoding utf8
}

function Resolve-PrivatePath([hashtable]$SyncMap, [string]$PublicPath) {
  if ($SyncMap.ContainsKey($PublicPath)) {
    $mapped = $SyncMap[$PublicPath]
    if ($mapped.EndsWith("/")) {
      return $mapped + [System.IO.Path]::GetFileName($PublicPath)
    }
    return $mapped
  }
  if ($SyncMap.ContainsKey(".")) {
    $rootMap = $SyncMap["."]
    if ($rootMap.EndsWith("/")) {
      return $rootMap + $PublicPath
    }
    return "$rootMap/$PublicPath"
  }
  return $null
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
$syncMap = Get-YamlBlockMap $forgeYaml "sync_map"
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

if ($DryRun) {
  Write-Host "[dry-run] Would import $MergeCommit from $publicRepoFull into $(git branch --show-current)"
  Write-Host "[dry-run] Would map public repo paths into $srcDir/"
  Write-Host "[dry-run] Would append task stub '$taskId' to docs/forge/TASKS.yaml if missing"
  exit 0
}

$baseCommit = "$MergeCommit^"
if ($parentCount -gt 1) {
  $baseCommit = "$MergeCommit^1"
}

$changedLines = git diff --name-status $baseCommit $MergeCommit
$unmapped = @()
foreach ($line in $changedLines) {
  $parts = $line -split "`t"
  $status = $parts[0]
  $code = $status -replace '\d', ''
  if ($code -eq "R") {
    if (-not (Resolve-PrivatePath $syncMap $parts[1])) { $unmapped += $parts[1] }
    if (-not (Resolve-PrivatePath $syncMap $parts[2])) { $unmapped += $parts[2] }
  } else {
    if (-not (Resolve-PrivatePath $syncMap $parts[1])) { $unmapped += $parts[1] }
  }
}
if ($unmapped.Count -gt 0) {
  Write-Error ("Unmapped public paths in merge {0}: {1}" -f $MergeCommit, ($unmapped -join ", "))
  exit 1
}

foreach ($line in $changedLines) {
  $parts = $line -split "`t"
  $status = $parts[0]
  $code = $status -replace '\d', ''
  switch ($code) {
    "A" {
      $privatePath = Resolve-PrivatePath $syncMap $parts[1]
      New-Item -ItemType Directory -Path (Split-Path -Parent $privatePath) -Force | Out-Null
      git show "$MergeCommit:$($parts[1])" | Set-Content -Path $privatePath -Encoding utf8
      git add $privatePath
    }
    "M" {
      $privatePath = Resolve-PrivatePath $syncMap $parts[1]
      New-Item -ItemType Directory -Path (Split-Path -Parent $privatePath) -Force | Out-Null
      git show "$MergeCommit:$($parts[1])" | Set-Content -Path $privatePath -Encoding utf8
      git add $privatePath
    }
    "T" {
      $privatePath = Resolve-PrivatePath $syncMap $parts[1]
      New-Item -ItemType Directory -Path (Split-Path -Parent $privatePath) -Force | Out-Null
      git show "$MergeCommit:$($parts[1])" | Set-Content -Path $privatePath -Encoding utf8
      git add $privatePath
    }
    "D" {
      $privatePath = Resolve-PrivatePath $syncMap $parts[1]
      git rm -f $privatePath 2>$null | Out-Null
      Remove-Item -Force $privatePath -ErrorAction SilentlyContinue
    }
    "R" {
      $oldPrivatePath = Resolve-PrivatePath $syncMap $parts[1]
      $newPrivatePath = Resolve-PrivatePath $syncMap $parts[2]
      if ($oldPrivatePath -ne $newPrivatePath) {
        git rm -f $oldPrivatePath 2>$null | Out-Null
        Remove-Item -Force $oldPrivatePath -ErrorAction SilentlyContinue
      }
      New-Item -ItemType Directory -Path (Split-Path -Parent $newPrivatePath) -Force | Out-Null
      git show "$MergeCommit:$($parts[2])" | Set-Content -Path $newPrivatePath -Encoding utf8
      git add $newPrivatePath
    }
    default {
      Write-Error "Unsupported git diff status '$status'."
      exit 1
    }
  }
}

Add-TaskStub (Join-Path (Get-Location) "docs/forge/TASKS.yaml") $taskId $taskDesc
Set-LastImportedCommit $forgeYaml $MergeCommit
git add $forgeYaml
if (Test-Path (Join-Path (Get-Location) "docs/forge/TASKS.yaml")) {
  git add (Join-Path (Get-Location) "docs/forge/TASKS.yaml")
}

Write-Host ""
Write-Host "Imported public change into the working tree without committing."
Write-Host "Next steps:"
Write-Host "  1. Review and test the imported change."
Write-Host "  2. Complete the intake task '$taskId' in docs/forge/TASKS.yaml."
Write-Host "  3. Commit it under normal FORGE governance."
