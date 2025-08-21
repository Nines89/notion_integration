$appName = "notion"
$serverProcess = $null
$alreadyTriggered = $false

while ($true) {
    $notionProcess = Get-Process -Name $appName -ErrorAction SilentlyContinue

    if ($notionProcess -and -not $alreadyTriggered) {
        # Avvia il .bat e salva il processo del server
        $serverProcess = Start-Process -FilePath "python" -ArgumentList "C:\Users\User\Desktop\notion_integration\notion_integration\file_server\notionFileServer.pyw" -PassThru
        $alreadyTriggered = $true
        Write-Host "Notion rilevato, server avviato"
    }
    elseif (-not $notionProcess -and $alreadyTriggered) {
        # Chiude il server se era stato avviato
        if ($serverProcess -and !$serverProcess.HasExited) {
            $serverProcess.Kill()
            Write-Host "Notion chiuso, server terminato"
        }
        $alreadyTriggered = $false
        $serverProcess = $null
    }

    Start-Sleep -Seconds 5
}
