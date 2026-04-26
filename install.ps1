param(
  [switch]$Force,
  [ValidateSet("copy", "link")]
  [string]$Mode = $(if ($env:FORGE_INSTALL_MODE) { $env:FORGE_INSTALL_MODE } else { "copy" }),
  [string[]]$Agent = @("shared")
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Join-Path $ScriptDir "skills\forge"

function Resolve-ForgeTargetRoot([string]$AgentName) {
  if ($env:FORGE_SKILL_TARGET) { return $env:FORGE_SKILL_TARGET }

  switch ($AgentName) {
    "shared" { return (Join-Path $HOME ".agents\skills") }
    "claude" { return (Join-Path $HOME ".claude\skills") }
    "claude-code" { return (Join-Path $HOME ".claude\skills") }
    "codex" { return (Join-Path $HOME ".codex\skills") }
    "cursor" { return (Join-Path $HOME ".cursor\skills") }
    "windsurf" { return (Join-Path $HOME ".windsurf\skills") }
    default { throw "FORGE: unknown agent target '$AgentName'" }
  }
}

if (-not (Test-Path $SourceDir)) {
  Write-Error "FORGE: skill source directory not found: $SourceDir"
  exit 1
}

foreach ($AgentName in $Agent) {
  $TargetRoot = Resolve-ForgeTargetRoot $AgentName
  $TargetDir = Join-Path $TargetRoot "forge"

  if ((Test-Path $TargetDir) -and -not $Force) {
    Write-Host "FORGE: skill already installed at $TargetDir"
    Write-Host "  Re-run with -Force to replace it."
    continue
  }

  New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
  if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
  }

  if ($Mode -eq "link") {
    New-Item -ItemType SymbolicLink -Path $TargetDir -Target $SourceDir | Out-Null
    Write-Host "FORGE: linked skill pack to $TargetDir"
  } else {
    Copy-Item -Recurse -Force $SourceDir $TargetDir
    Write-Host "FORGE: installed skill pack to $TargetDir"
  }
}

Write-Host ""
foreach ($AgentName in $Agent) {
  $TargetRoot = Resolve-ForgeTargetRoot $AgentName
  $TargetDir = Join-Path $TargetRoot "forge"
  $Required = @(
    "SKILL.md",
    "bootstrap\SKILL.md",
    "execute-task\SKILL.md",
    "critique\SKILL.md",
    "security-review\SKILL.md",
    "evaluation\SKILL.md",
    "memory\SKILL.md",
    "assets\templates\AI.md",
    "assets\templates\TASKS.yaml"
  )

  if (-not (Test-Path $TargetDir)) {
    Write-Error "FORGE: not installed at $TargetDir"
    exit 1
  }

  foreach ($RelativePath in $Required) {
    $Path = Join-Path $TargetDir $RelativePath
    if (-not (Test-Path $Path)) {
      Write-Error "FORGE: missing installed file: $Path"
      exit 1
    }
  }

  Write-Host "FORGE: install looks good at $TargetDir"
}

Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open your project in a skill-aware agent."
Write-Host "  2. Ask it to use the 'forge' skill."
Write-Host "  3. In slash-command IDEs, subskills are grouped as /forge-*."
Write-Host "  4. If the repo has no FORGE docs yet, start with:"
Write-Host "     Use the forge skill or /forge-bootstrap to create docs/forge for this project."
