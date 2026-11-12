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
Paso "1/9 Programas: Node.js, Git, Python 3.12 y FFmpeg (con winget, el instalador de Windows)"
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
# Claude Code: es la IA que dirige el montaje (necesita una suscripción de Claude; la primera vez pide entrar)
if (Get-Command claude -ErrorAction SilentlyContinue) { Ok "Claude Code ya estaba" }
else {
    Write-Host "   instalando Claude Code..."
    npm install -g @anthropic-ai/claude-code --silent
    RefrescarPath
    if (Get-Command claude -ErrorAction SilentlyContinue) { Ok "Claude Code" } else { Aviso "Claude Code no aparece todavía: abre otra ventana y lanza 'claude' para comprobarlo" }
}

# 2. Entorno de Python -----------------------------------------------------------------------------------------
Paso "2/9 Entorno de Python propio en .venv (no toca el Python del sistema)"
$PY = Join-Path $REPO ".venv\Scripts\python.exe"
if (-not (Test-Path $PY)) { & py -3.12 -m venv .venv; Ok "creado .venv" } else { Ok ".venv ya estaba" }
Write-Host "   instalando librerías (la primera vez tarda unos minutos)..."
& $PY -m pip install --upgrade pip --quiet
& $PY -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "Falló pip install. Mira el error de arriba." -ForegroundColor Red; exit 1 }
Ok "librerías instaladas"

# 3. VectCutAPI (escribe proyectos de CapCut) -------------------------------------------------------------------
Paso "3/9 VectCutAPI en vendor\VectCutAPI (la pieza que escribe proyectos de CapCut)"
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
Paso "4/9 Modelos de MediaPipe (recorte de la persona y detección de manos), de los servidores de Google"
New-Item -ItemType Directory -Force (Join-Path $REPO "modelos") | Out-Null
Descargar "https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_segmenter/float16/latest/selfie_segmenter.tflite" (Join-Path $REPO "modelos\selfie_segmenter.tflite")
Descargar "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task" (Join-Path $REPO "modelos\hand_landmarker.task")
Descargar "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite" (Join-Path $REPO "modelos\blaze_face_short_range.tflite")

# 5. Fuentes ---------------------------------------------------------------------------------------------------
Paso "5/9 Fuentes libres (licencia OFL): Anton, Bebas Neue y Archivo Black, de Google Fonts"
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
Paso "6/9 Tu configuración (config.json) y carpeta de trabajo"
if (-not (Test-Path "config.json")) { Copy-Item "config.ejemplo.json" "config.json"; Ok "creado config.json (edítalo si quieres cambiar colores o carpetas)" } else { Ok "config.json ya estaba: no lo toco" }
if (-not (Test-Path ".env")) { Copy-Item ".env.ejemplo" ".env"; Ok "creado .env (pon ahí tu PEXELS_API_KEY si vas a buscar B-roll)" } else { Ok ".env ya estaba: no lo toco" }
foreach ($d in @("trabajo", "trabajo\transcripciones", "trabajo\piezas", "mi-estilo\referencias")) { New-Item -ItemType Directory -Force (Join-Path $REPO $d) | Out-Null }
# El catálogo de recursos es de cada uno (no se sube a git): se parte del de ejemplo
if (-not (Test-Path "mi-estilo\estilo.md")) { Copy-Item "mi-estilo\estilo.ejemplo.md" "mi-estilo\estilo.md"; Ok "creado mi-estilo\estilo.md (rellénalo con tu estilo)" } else { Ok "mi-estilo\estilo.md ya estaba: no lo toco" }
if (-not (Test-Path "mi-estilo\recursos.md")) { Copy-Item "mi-estilo\recursos.ejemplo.md" "mi-estilo\recursos.md"; Ok "creado mi-estilo\recursos.md (tu catálogo de recursos, desde el de ejemplo)" } else { Ok "mi-estilo\recursos.md ya estaba: no lo toco" }
Ok "carpetas de trabajo listas"

# 6b. El motor ---------------------------------------------------------------------------------------------------
# Lo que monta el vídeo terminado sin CapCut (specs/2026-11-12-compartir-para-novatos.md). Mismas versiones que el
# PC donde se montaron los reels. Todo va dentro de esta carpeta, salvo tus vídeos (en Vídeos\Reels).
Paso "7/9 El motor: limpieza de voz, transcripción, render y sonidos (la primera vez tarda 10-20 minutos)"
$tiene311 = $false
try { $null = & py -3.11 -c "print(1)" 2>$null; $tiene311 = ($LASTEXITCODE -eq 0) } catch { $tiene311 = $false }
if ($tiene311) { Ok "Python 3.11 ya estaba" }
else {
    Write-Host "   instalando Python 3.11 (la limpieza de voz no funciona con la 3.12)..."
    winget install --id Python.Python.3.11 -e --silent --accept-source-agreements --accept-package-agreements
    RefrescarPath
}
$rutasChrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
                 "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe")
if ($rutasChrome | Where-Object { Test-Path $_ }) { Ok "Chrome ya estaba" }
else {
    Write-Host "   instalando Google Chrome (el motor dibuja cada fotograma con él, sin abrir ventanas)..."
    winget install --id Google.Chrome -e --silent --accept-source-agreements --accept-package-agreements
}
$PYDF = Join-Path $REPO ".venv-df\Scripts\python.exe"
if (-not (Test-Path $PYDF)) { & py -3.11 -m venv .venv-df; Ok "creado .venv-df" }
Write-Host "   librerías de la limpieza de voz (DeepFilterNet, unos 800 MB)..."
& $PYDF -m pip install --upgrade pip --quiet
& $PYDF -m pip install --quiet --extra-index-url https://download.pytorch.org/whl/cpu `
    torch==2.5.1+cpu torchaudio==2.5.1+cpu numpy==1.26.4 soundfile==0.14.0 deepfilternet==0.5.6
if ($LASTEXITCODE -ne 0) { Write-Host "Falló la instalación de la limpieza de voz. Mira el error de arriba." -ForegroundColor Red; exit 1 }
Ok "limpieza de voz"
$PYFW = Join-Path $REPO ".venv-fw\Scripts\python.exe"
if (-not (Test-Path $PYFW)) { & py -3.12 -m venv .venv-fw; Ok "creado .venv-fw" }
& $PYFW -m pip install --upgrade pip --quiet
& $PYFW -m pip install --quiet faster-whisper==1.2.1
if ($LASTEXITCODE -ne 0) { Write-Host "Falló la instalación de la transcripción. Mira el error de arriba." -ForegroundColor Red; exit 1 }
Ok "transcripción (faster-whisper)"
$HM = Join-Path $REPO "vendor\huashu-motion"
# Fijado al commit de la etiqueta v0.3.1 (una etiqueta se puede mover; un commit no), y comprobado en cada vuelta
$HMCOMMIT = "52467f99c602b76ba86d511d37acdfe93fa1e16e"
if (-not (Test-Path (Join-Path $HM ".git"))) { git clone --quiet https://github.com/alchaincyf/huashu-motion.git $HM }
git -C $HM fetch --quiet origin
git -C $HM checkout --quiet $HMCOMMIT
if ((git -C $HM rev-parse HEAD) -ne $HMCOMMIT) { Write-Host "huashu-motion no está en la versión probada. Borra vendor\huashu-motion y vuelve a lanzar." -ForegroundColor Red; exit 1 }
Ok "render (huashu-motion 0.3.1, la versión probada, $($HMCOMMIT.Substring(0,7)))"
# Tus carpetas de vídeo, con la misma forma que las de los reels de ejemplo
$REELS = Join-Path ([Environment]::GetFolderPath("MyVideos")) "Reels"
$RECURSOS = Join-Path $REELS "3 RECURSOS"
foreach ($d in @("1 TOMAS EN BRUTO", "2 PARA SUBIR", "3 RECURSOS\MUSICA", "motor-datos\fichas", "motor-datos\voz", "motor-datos\perfil")) {
    New-Item -ItemType Directory -Force (Join-Path $REELS $d) | Out-Null
}
$CFGM = Join-Path $REPO "motor\config.json"
if (-not (Test-Path $CFGM)) {
    $b = { param($p) $p.Replace('\', '/') }
    $cfgMotor = [ordered]@{
        carpeta_contenido     = & $b $REELS
        carpeta_tomas         = & $b (Join-Path $REELS "1 TOMAS EN BRUTO")
        carpeta_reutilizables = & $b $RECURSOS
        carpeta_datos         = & $b (Join-Path $REELS "motor-datos")
        carpeta_render        = & $b (Join-Path $HOME "reels-render")
        carpeta_salida        = & $b (Join-Path $REELS "2 PARA SUBIR")
        om                    = & $b (Join-Path $REPO "motor\om")
        python_df             = & $b $PYDF
        python_fw             = & $b $PYFW
    }
    [IO.File]::WriteAllText($CFGM, ($cfgMotor | ConvertTo-Json), (New-Object Text.UTF8Encoding($false)))
    Ok "creado motor\config.json (tus vídeos van en $REELS)"
} else { Ok "motor\config.json ya estaba: no lo toco" }
# Efectos y música libres de Mixkit (mixkit.co/license). Se bajan a TU ordenador: su licencia no deja repartirlos sueltos.
$sfx = [ordered]@{ "SFX-P-golpe" = 2180; "SFX-P-golpe-grave" = 1143; "SFX-P-barrido" = 175; "SFX-P-absorcion" = 784; "SFX-P-subida" = 790;
                   "SFX-P-latido" = 498; "SFX-P-silbato" = 615; "SFX-P-tic" = 2568; "SFX-P-cierre" = 951; "SFX-P-grada" = 2111 }
foreach ($k in $sfx.Keys) {
    $wav = Join-Path $RECURSOS "$k.wav"
    if (Test-Path $wav) { continue }
    $mp3 = Join-Path $env:TEMP "$k.mp3"
    try {
        Invoke-WebRequest -Uri "https://assets.mixkit.co/active_storage/sfx/$($sfx[$k])/$($sfx[$k])-preview.mp3" -OutFile $mp3 -UseBasicParsing
        & ffmpeg -v error -y -i $mp3 $wav; Remove-Item $mp3 -ErrorAction SilentlyContinue
    } catch { Aviso "no pude bajar $k (el montaje sale igual, sin ese efecto)" }
}
$musica = [ordered]@{ "M-la-raiz-indie-rock" = 1157; "M-dare-me-indie-rock" = 1135; "M-a-game-electro" = 777; "M-i-do-edm-optimista" = 1001;
                      "M-karma-dance-pop" = 1183; "M-heartbeat-indie-pop" = 1000; "M-better-times-synthpop" = 173;
                      "M-driving-ambition-emotiva" = 32; "M-dreaming-big-emotiva" = 31 }
foreach ($k in $musica.Keys) {
    $mp3 = Join-Path $RECURSOS "MUSICA\$k.mp3"
    if (Test-Path $mp3) { continue }
    try { Invoke-WebRequest -Uri "https://assets.mixkit.co/music/$($musica[$k])/$($musica[$k]).mp3" -OutFile $mp3 -UseBasicParsing }
    catch { Aviso "no pude bajar la música $k" }
}
Ok "efectos y música de Mixkit en $RECURSOS"

# 7. Skill para Claude Code ------------------------------------------------------------------------------------
Paso "8/9 Skill 'montar-reels' para Claude Code (en $HOME\.claude\skills\montar-reels)"
$SK = Join-Path $HOME ".claude\skills\montar-reels"
New-Item -ItemType Directory -Force $SK | Out-Null
$texto = [IO.File]::ReadAllText((Join-Path $REPO "skill\SKILL.md"), [Text.Encoding]::UTF8).Replace("{{REPO}}", $REPO)
[IO.File]::WriteAllText((Join-Path $SK "SKILL.md"), $texto, (New-Object Text.UTF8Encoding($false)))
Ok "skill copiada y apuntando a $REPO"
# Los agentes director (decide el montaje) y revisor (juzga el export), para cualquier carpeta de Claude Code
$AG = Join-Path $HOME ".claude\agents"
New-Item -ItemType Directory -Force $AG | Out-Null
foreach ($a in Get-ChildItem (Join-Path $REPO ".claude\agents") -Filter *.md) {
    $texto = [IO.File]::ReadAllText($a.FullName, [Text.Encoding]::UTF8).Replace("{{REPO}}", $REPO)
    [IO.File]::WriteAllText((Join-Path $AG $a.Name), $texto, (New-Object Text.UTF8Encoding($false)))
    Ok "agente $($a.BaseName)"
}
# El puente con Negocio (specs/2026-10-12-puente-negocio.md): una clave propia de este PC y que arranque solo
# con Windows. La clave se pega una vez en Negocio; sin ella el puente no hace nada.
$cfg = [IO.File]::ReadAllText((Join-Path $REPO "config.json"), [Text.Encoding]::UTF8) | ConvertFrom-Json
if (-not $cfg.puente_clave) {
    $bytes = New-Object byte[] 18; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $clave = [Convert]::ToBase64String($bytes).Replace("+", "-").Replace("/", "_")
    $cfg | Add-Member -NotePropertyName puente_clave -NotePropertyValue $clave -Force
    [IO.File]::WriteAllText((Join-Path $REPO "config.json"), ($cfg | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
    Ok "clave del puente creada"
}
$inicio = Join-Path ([Environment]::GetFolderPath("Startup")) "Puente montar-reels.lnk"
$atajo = (New-Object -ComObject WScript.Shell).CreateShortcut($inicio)
$atajo.TargetPath = "powershell.exe"
$atajo.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$(Join-Path $REPO 'puente.ps1')`""
$atajo.WorkingDirectory = $REPO
$atajo.Save()
Ok "el puente arrancará solo con Windows. Tu clave para Negocio: $((Get-Content (Join-Path $REPO 'config.json') -Raw | ConvertFrom-Json).puente_clave)"

# 8. Comprobación ----------------------------------------------------------------------------------------------
Paso "9/9 Comprobación"
Push-Location (Join-Path $REPO "scripts")
& $PY -c "import config, pyJianYingDraft, mediapipe, faster_whisper, cv2; print('   ok: las librerías se cargan')"
$fallo = $LASTEXITCODE
Pop-Location
if ($fallo -ne 0) { Aviso "algo no carga (mira el error de arriba)"; exit 1 }
& $PYDF -c "import df.enhance; print('   ok: la limpieza de voz se carga')"
if ($LASTEXITCODE -ne 0) { Aviso "la limpieza de voz no carga (mira el error de arriba)"; exit 1 }
& $PYFW -c "import faster_whisper; print('   ok: la transcripción se carga')"
if ($LASTEXITCODE -ne 0) { Aviso "la transcripción no carga (mira el error de arriba)"; exit 1 }
& ffmpeg -hide_banner -version | Select-Object -First 1

Write-Host ""
Write-Host "Instalación terminada. Ahora lo compruebo todo:" -ForegroundColor Green
& (Join-Path $REPO "comprobar.ps1")
