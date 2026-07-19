<#
.SYNOPSIS
    Windows global wrapper for Storm Framework.
.DESCRIPTION
    Execute storm-framework containers with proper mount, network, and kernel capabilities.
    Use Administrator mode (Run as Admin) to enable sniffing/raw socket capabilities.
#>

$AppHome = "/opt/storm-framework"
$DockerImage = "zxelzy/storm-framework:latest"

# Interception of Copy CA Certificate Command
if ($args.Count -eq 2 -and $args[0] -eq "-cp" -and $args[1] -eq "-crt") {
    # $HOME path resolution (C:\Users\Username)
    $TargetHome = [System.Environment]::GetFolderPath("UserProfile")
    $TargetFile = Join-Path $TargetHome "smf_ca.crt"

    # Docker pipe execution.
    $ExtractCmd = "docker run --rm -v storm_data:${AppHome}/data ${DockerImage} cat ${AppHome}/data/smf_ca.crt > `"$TargetFile`""
    cmd.exe /c $ExtractCmd

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[*] Certificate successfully copied to: $TargetFile" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[*] Failed to copy CA" -ForegroundColor Red
        exit 1
    }
}

# Privilege escalation detection (Equivalent to EUID == 0)
$CurrentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$CurrentPrincipal = [Security.Principal.WindowsPrincipal]::new($CurrentIdentity)
$IsAdmin = $CurrentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

$PrivFlags = @()
if ($IsAdmin) {
    # Kernel capability injection if run via PowerShell Administrator
    $PrivFlags += "--cap-add=NET_ADMIN"
    $PrivFlags += "--cap-add=NET_RAW"
    $PrivFlags += "--cap-add=SYS_ADMIN"
}

# Parsing Main Arguments
if ($args.Count -eq 0) {
    $CmdArgs = @("./smfstart")
} else {
    $CmdArgs = $args
}

# Docker Argument Construction
$DockerArgs = @(
    "run", "-it", "--rm",
    "--network", "host"
)

$DockerArgs += $PrivFlags
$DockerArgs += "-v", "storm_data:${AppHome}/data"

# Use .ProviderPath so that the Windows path (C:\...)
$DockerArgs += "-v", "$($PWD.ProviderPath):/workspace"
$DockerArgs += "-w", "/workspace"
$DockerArgs += $DockerImage
$DockerArgs += $CmdArgs

# Execution
& docker $DockerArgs

