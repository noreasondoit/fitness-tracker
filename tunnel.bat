@echo off
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 80:localhost:5000 nokey@localhost.run 2> "%USERPROFILE%\dev\fitness-tracker\tunnel-output.txt"
