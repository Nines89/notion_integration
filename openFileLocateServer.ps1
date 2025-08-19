$appName = "notion"
$alreadyTriggered = $false

while ($true) {
    $process = Get-Process -Name $appName -ErrorAction SilentlyContinue
    if ($process -and -not $alreadyTriggered) {
        # Lancia il task desiderato
        Start-Process -FilePath "C:\Users\User\Desktop\file_integration\pravaBat.bat"
        $alreadyTriggered = $true
    }
    elseif (-not $process) {
        $alreadyTriggered = $false
    }
    Start-Sleep -Seconds 5
}
