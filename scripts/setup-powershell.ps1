# ===================================================
# Security Hub - PowerShell Setup
# ===================================================
# Add this to your PowerShell profile for easy access

# Set Python path
$env:PYTHON_PATH = "C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe"

# Create convenient aliases for running scripts
function replay-attack {
    & $env:PYTHON_PATH replay_attack.py @args
}

function replay-detector {
    & $env:PYTHON_PATH replay_detector.py @args
}

function attack-compare {
    & $env:PYTHON_PATH attack_comparator.py @args
}

function data-collect {
    & $env:PYTHON_PATH data_collector.py @args
}

function dos-attack {
    & $env:PYTHON_PATH dos_attack.py @args
}

# Set working directory
Set-Location "C:\Users\Test\Downloads\Security_hub\Security_hub\Security_hub"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  🛡️  Security Hub - PowerShell Environment" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Python location: $env:PYTHON_PATH" -ForegroundColor Yellow
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  replay-attack       - Run replay attack simulator" -ForegroundColor White
Write-Host "  replay-detector     - Run replay attack detector" -ForegroundColor White
Write-Host "  attack-compare      - Run attack comparator" -ForegroundColor White
Write-Host "  data-collect        - Run data collector" -ForegroundColor White
Write-Host "  dos-attack          - Run DoS attack simulator" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
