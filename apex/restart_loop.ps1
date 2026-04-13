# Windows restart loop for APEX agent
while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] Starting APEX agent..."
    
    # Run apex_live.py and capture output
    python apex_live.py 2>&1 | Tee-Object -FilePath "apex_loop.log" -Append
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Output "[$timestamp] Agent exited. Restarting in 10 seconds..."
    
    # Wait 10 seconds before restarting
    Start-Sleep -Seconds 10
}
