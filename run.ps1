param(
  [string]$ProjectDir = "."
)

$IMAGE = "insightforge:local"
$ErrorActionPreference = "Stop"

# Kiểm tra image đã build chưa
docker image inspect $IMAGE 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Write-Host "[InsightForge] Image chua duoc build. Chay truoc:"
  Write-Host "  docker build -t $IMAGE ."
  exit 1
}

# Auto-detect GPU
$gpuArgs = @()
Write-Host -NoNewline "[InsightForge] Detecting GPU... "
docker run --rm --gpus all --entrypoint true $IMAGE 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
  $gpuArgs = @("--gpus", "all")
  Write-Host "GPU OK (CUDA mode)"
} else {
  Write-Host "not found -> CPU mode"
}

# Resolve full path
if (-not (Test-Path $ProjectDir)) {
  Write-Host "[InsightForge] Khong tim thay thu muc: $ProjectDir"
  exit 1
}
$fullPath = Resolve-Path $ProjectDir

# Chạy insightforge
$dockerArgs = @(
  "run", "--rm", "-it"
) + $gpuArgs + @(
  "-v", "${fullPath}:/workspace",
  "-v", "insightforge_data:/root/.insightforge",
  "-e", "GITHUB_TOKEN=$env:GITHUB_TOKEN",
  $IMAGE, "/workspace"
)

docker @dockerArgs
