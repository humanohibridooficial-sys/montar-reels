# Enciende el puente con Negocio (specs/2026-10-12-puente-negocio.md), sin ventana. Lo lanza Windows al arrancar
# (acceso directo que crea instalar.ps1); también se puede lanzar a mano:  .\puente.ps1
$REPO = $PSScriptRoot
$cfg = Get-Content (Join-Path $REPO "config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
# El Python del editor: el de config.json ("python") si lo hay; si no, el .venv del repo que crea instalar.ps1.
$py = if ($cfg.python) { $cfg.python } else { Join-Path $REPO ".venv\Scripts\python.exe" }
$pyw = $py -replace "python\.exe$", "pythonw.exe"
if (-not (Test-Path $pyw)) { $pyw = $py }
$puerto = if ($cfg.puente_puerto) { $cfg.puente_puerto } else { 7810 }
# Si ya está encendido, no lo enciendo dos veces.
try { Invoke-WebRequest -Uri "http://127.0.0.1:$puerto/estado" -UseBasicParsing -TimeoutSec 2 | Out-Null; exit 0 } catch {}
Start-Process -FilePath $pyw -ArgumentList "`"$(Join-Path $REPO 'puente\puente.py')`"" -WorkingDirectory $REPO -WindowStyle Hidden
