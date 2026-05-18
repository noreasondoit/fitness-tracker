$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "C:\Windows\System32\OpenSSH\ssh.exe"
$psi.Arguments = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=30 -R 80:localhost:5000 nokey@localhost.run"
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$p = [System.Diagnostics.Process]::Start($psi)
$output = $p.StandardError.ReadToEnd()

$desktop = [Environment]::GetFolderPath("Desktop")
if ($output -match '(https://[a-f0-9]+\.lhr\.life)') {
    $url = $matches[1]
    $url | Set-Content -Path "$desktop\Fitness-Tracker-URL.txt" -Encoding UTF8
}
$p.WaitForExit()
