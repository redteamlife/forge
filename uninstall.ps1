param(
  [string[]]$Agent = @("shared")
)

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

foreach ($AgentName in $Agent) {
  $TargetRoot = Resolve-ForgeTargetRoot $AgentName
  $TargetDir = Join-Path $TargetRoot "forge"

  if (-not (Test-Path $TargetDir)) {
    Write-Host "FORGE: no installed skill pack found at $TargetDir"
    continue
  }

  Remove-Item -Recurse -Force $TargetDir
  Write-Host "FORGE: removed skill pack from $TargetDir"
}
