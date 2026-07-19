$ToolName = "storm.ps1"
$RepoName = "storm-framework"
$WrapperUrl = "https://raw.githubusercontent.com/StormWorld0/$RepoName/main/docker/bin/$ToolName"
$DockerImage = "zxelzy/$RepoName"

$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Host "[*] ERROR: PowerShell not Administrator" -ForegroundColor Red
    exit
}

# Pull docker images
docker pull $DockerImage
$TargetPath = Join-Path $env:windir "System32\$ToolName"

# Download the Windows wrapper
Invoke-WebRequest -Uri $WrapperUrl -OutFile $TargetPath

Write-Host "[✓] INSTALLATION COMPLETE" -ForegroundColor Green
