# start-tunnel.ps1 - SSH tunnel with real-time URL capture
$ErrorActionPreference = "Continue"
$desktop = [Environment]::GetFolderPath("Desktop")
$urlFile = Join-Path $desktop "Fitness-Tracker-URL.txt"
$logFile = Join-Path $env:USERPROFILE "dev\fitness-tracker\tunnel.log"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp Starting tunnel..." | Add-Content $logFile
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "ssh"
        $psi.Arguments = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:5000 nokey@localhost.run"
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $psi
        
        $sb = [System.Text.StringBuilder]::new()
        $event = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action {
            $line = $Event.SourceEventArgs.Data
            if ($line) {
                [void]$Event.MessageData.AppendLine($line)
                if ($line -match '(https://[a-f0-9]+\.lhr\.life)') {
                    $url = $matches[1]
                    "URL: $url" | Set-Content $Event.MessageData.Tag -Encoding UTF8
                    "$(Get-Date -Format 'HH:mm:ss') URL: $url" | Add-Content $Event.MessageData.Tag2
                }
            }
        } -MessageData @{ 
            Tag = $urlFile
            Tag2 = $logFile
            SB = $sb 
        }
        
        $process.Start() | Out-Null
        $process.BeginErrorReadLine()
        $process.WaitForExit()
        Unregister-Event -SourceIdentifier $event.Name -Force -ErrorAction SilentlyContinue
        
        "$(Get-Date -Format 'HH:mm:ss') Tunnel closed. Exit: $($process.ExitCode)" | Add-Content $logFile
    } catch {
        "$(Get-Date -Format 'HH:mm:ss') Error: $_" | Add-Content $logFile
    }
    "$(Get-Date -Format 'HH:mm:ss') Reconnecting in 10s..." | Add-Content $logFile
    Start-Sleep 10
}
