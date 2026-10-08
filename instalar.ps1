# Instalador del editor de reels. Se puede lanzar las veces que haga falta: lo que ya está, lo salta.
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\instalar.ps1
$ErrorActionPreference = "Stop"
$REPO = $PSScriptRoot
Set-Location $REPO

function Paso($t) { Write-Host ""; Write-Host "== $t" -ForegroundColor Cyan }
function Ok($t)   { Write-Host "   ok: $t" -ForegroundColor Green }
function Aviso($t){ Write-Host "   aviso: $t" -ForegroundColor Yellow }
function RefrescarPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Descargar($url, $destino) {
    if (Test-Path $destino) { Ok "ya estaba $(Split-Path $destino -Leaf)"; return }
    Write-Host "   descargando $(Split-Path $destino -Leaf)..."
    Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing
    Ok (Split-Path $destino -Leaf)
}

# 1. Programas del sistema --------------------------------------------------------------------------------------
Paso "1/8 Programas: Node.js, Git, Python 3.12 y FFmpeg (con winget, el instalador de Windows)"
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "No encuentro winget. Instala 'Instalador de aplicación' desde Microsoft Store y vuelve a lanzar este script." -ForegroundColor Red
    exit 1
}
$programas = @(
    @{ id = "OpenJS.NodeJS.LTS"; cmd = "node" },
    @{ id = "Git.Git";           cmd = "git" },
    @{ id = "Python.Python.3.12"; cmd = "py" },
    @{ id = "Gyan.FFmpeg";       cmd = "ffmpeg" }
)
foreach ($p in $programas) {
    if (Get-Command $p.cmd -ErrorAction SilentlyContinue) {
        if ($p.id -eq "Python.Python.3.12") {
            $tiene312 = $false
            try { $null = & py -3.12 -c "print(1)" 2>$null; $tiene312 = ($LASTEXITCODE -eq 0) } catch { $tiene312 = $false }
            if ($tiene312) { Ok "Python 3.12 ya estaba"; continue }
        } else { Ok "$($p.cmd) ya estaba"; continue }
    }
    Write-Host "   instalando $($p.id)..."
    winget install --id $p.id -e --silent --accept-source-agreements --accept-package-agreements
    RefrescarPath
}
RefrescarPath
foreach ($c in @("node", "git", "py", "ffmpeg")) {
    if (-not (Get-Command $c -ErrorAction SilentlyContinue)) {
        Aviso "$c no aparece todavía. Cierra esta ventana de PowerShell, abre otra y vuelve a lanzar .\instalar.ps1"
        exit 1
    }
}

# 2. Entorno de Python -----------------------------------------------------------------------------------------
Paso "2/8 Entorno de Python propio en .venv (no toca el Python del sistema)"
$PY = Join-Path $REPO ".venv\Scripts\python.exe"
if (-not (Test-Path $PY)) { & py -3.12 -m venv .venv; Ok "creado .venv" } else { Ok ".venv ya estaba" }
Write-Host "   instalando librerías (la primera vez tarda unos minutos)..."
& $PY -m pip install --upgrade pip --quiet
& $PY -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "Falló pip install. Mira el error de arriba." -ForegroundColor Red; exit 1 }
Ok "librerías instaladas"

# 3. VectCutAPI (escribe proyectos de CapCut) -------------------------------------------------------------------
Paso "3/8 VectCutAPI en vendor\VectCutAPI (la pieza que escribe proyectos de CapCut)"
$VC = Join-Path $REPO "vendor\VectCutAPI"
$COMMIT = "cfa4779a52f1dc59a56d90cc5868778eb50c6a97"
if (-not (Test-Path (Join-Path $VC ".git"))) {
    New-Item -ItemType Directory -Force (Join-Path $REPO "vendor") | Out-Null
    git clone --quiet https://github.com/sun-guannan/VectCutAPI.git $VC
}
git -C $VC fetch --quiet origin
git -C $VC checkout --quiet $COMMIT
Ok "VectCutAPI en la versión probada ($($COMMIT.Substring(0,7)))"

# 4. Modelos de MediaPipe --------------------------------------------------------------------------------------
Paso "4/8 Modelos de MediaPipe (recorte de la persona y detección de manos), de los servidores de Google"
New-Item -ItemType Directory -Force (Join-Path $REPO "modelos") | Out-Null
Descargar "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite" (Join-Path $REPO "modelos\selfie_segmenter.tflite")
Descargar "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task" (Join-Path $REPO "modelos\hand_landmarker.task")

# 5. Fuentes ---------------------------------------------------------------------------------------------------
Paso "5/8 Fuentes libres (licencia OFL): Anton, Bebas Neue y Archivo Black, de Google Fonts"
$F = Join-Path $REPO "fuentes"
New-Item -ItemType Directory -Force $F | Out-Null
$GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"
Descargar "$GF/anton/Anton-Regular.ttf"             (Join-Path $F "Anton-Regular.ttf")
Descargar "$GF/anton/OFL.txt"                       (Join-Path $F "OFL-Anton.txt")
Descargar "$GF/bebasneue/BebasNeue-Regular.ttf"     (Join-Path $F "BebasNeue-Regular.ttf")
Descargar "$GF/bebasneue/OFL.txt"                   (Join-Path $F "OFL-BebasNeue.txt")
Descargar "$GF/archivoblack/ArchivoBlack-Regular.ttf" (Join-Path $F "ArchivoBlack-Regular.ttf")
Descargar "$GF/archivoblack/OFL.txt"                (Join-Path $F "OFL-ArchivoBlack.txt")

# 6. Configuración ---------------------------------------------------------------------------------------------
Paso "6/8 Tu configuración (config.json) y carpeta de trabajo"
if (-not (Test-Path "config.json")) { Copy-Item "config.ejemplo.json" "config.json"; Ok "creado config.json (edítalo si quieres cambiar colores o carpetas)" } else { Ok "config.json ya estaba: no lo toco" }
if (-not (Test-Path ".env")) { Copy-Item ".env.ejemplo" ".env"; Ok "creado .env (pon ahí tu PEXELS_API_KEY si vas a buscar B-roll)" } else { Ok ".env ya estaba: no lo toco" }
foreach ($d in @("trabajo", "trabajo\transcripciones", "trabajo\piezas", "mi-estilo\referencias")) { New-Item -ItemType Directory -Force (Join-Path $REPO $d) | Out-Null }
Ok "carpetas de trabajo listas"

# 7. Skill para Claude Code ------------------------------------------------------------------------------------
Paso "7/8 Skill 'montar-reels' para Claude Code (en $HOME\.claude\skills\montar-reels)"
$SK = Join-Path $HOME ".claude\skills\montar-reels"
New-Item -ItemType Directory -Force $SK | Out-Null
$texto = [IO.File]::ReadAllText((Join-Path $REPO "skill\SKILL.md"), [Text.Encoding]::UTF8).Replace("{{REPO}}", $REPO)
[IO.File]::WriteAllText((Join-Path $SK "SKILL.md"), $texto, (New-Object Text.UTF8Encoding($false)))
Ok "skill copiada y apuntando a $REPO"

# 8. Comprobación ----------------------------------------------------------------------------------------------
Paso "8/8 Comprobación"
Push-Location (Join-Path $REPO "scripts")
& $PY -c "import config, pyJianYingDraft, mediapipe, faster_whisper, cv2; print('   ok: las librerías se cargan')"
$fallo = $LASTEXITCODE
Pop-Location
if ($fallo -ne 0) { Aviso "algo no carga (mira el error de arriba)"; exit 1 }
& ffmpeg -hide_banner -version | Select-Object -First 1

Write-Host ""
Write-Host "Instalación terminada." -ForegroundColor Green
Write-Host "Falta UNA cosa a mano: abre CapCut, crea un proyecto vacío, llámalo PLANTILLA-REELS y cierra CapCut."
Write-Host "Después abre Claude Code en esta carpeta y dile: 'edita este reel' con la ruta de tu vídeo."
