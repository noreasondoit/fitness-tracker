$desktop = [Environment]::GetFolderPath("Desktop")
$urlFile = Join-Path $desktop "Fitness-Tracker-URL.txt"

while ($true) {
    try {
        $output = ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:5000 nokey@localhost.run 2>&1
        
        # Extract URL like https://xxxx.lhr.life
        if ($output -match '(https://[a-f0-9]+\.lhr\.life)') {
            $url = $matches[1]
            "Current URL: $url" | Set-Content -Path $urlFile -Encoding UTF8
            Write-Host "Tunnel: $url"
        }
    } catch {
        Write-Host "Tunnel crashed, retrying in 5s... $_"
    }
    Start-Sleep 5
}
