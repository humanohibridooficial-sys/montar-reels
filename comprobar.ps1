# Comprueba que el editor está listo en este equipo. Se puede lanzar cuando quieras; no cambia nada.
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\comprobar.ps1
# Si usas otro Python (no el .venv del instalador), ponlo en la variable MONTAR_REELS_PY.
$REPO = $PSScriptRoot
$fallos = 0; $avisos = 0
function Bien($t)  { Write-Host "  ok     $t" -ForegroundColor Green }
function Mal($t, $arreglo) { Write-Host "  FALTA  $t" -ForegroundColor Red; Write-Host "         -> $arreglo" -ForegroundColor Gray; $script:fallos++ }
function Ojo($t, $arreglo) { Write-Host "  aviso  $t" -ForegroundColor Yellow; if ($arreglo) { Write-Host "         -> $arreglo" -ForegroundColor Gray }; $script:avisos++ }
function Hay($p) { Test-Path -LiteralPath $p }

Write-Host ""; Write-Host "Comprobando el editor de reels en $REPO" -ForegroundColor Cyan

# 1. Programas
foreach ($p in @("ffmpeg", "ffprobe", "git")) {
    if (Get-Command $p -ErrorAction SilentlyContinue) { Bien $p } else { Mal $p "vuelve a lanzar .\instalar.ps1 (lo instala con winget) y abre una terminal nueva" }
}
if (Get-Command claude -ErrorAction SilentlyContinue) { Bien "Claude Code" } else { Mal "Claude Code (el comando 'claude')" "instálalo con: npm install -g @anthropic-ai/claude-code  (necesita una suscripción de Claude)" }

# 2. Python y librerías
$PY = if ($env:MONTAR_REELS_PY) { $env:MONTAR_REELS_PY } else { Join-Path $REPO ".venv\Scripts\python.exe" }
if (Hay $PY) {
    Bien "Python del editor ($PY)"
    Push-Location (Join-Path $REPO "scripts")
    $faltan = & $PY -c "import importlib.util, config; print(' '.join(m for m in ['pyJianYingDraft','mediapipe','cv2','faster_whisper','PIL'] if importlib.util.find_spec(m) is None))" 2>$null
    if ($LASTEXITCODE -ne 0) { Mal "el Python del editor no arranca" "vuelve a lanzar .\instalar.ps1 (paso 2)" }
    elseif (-not $faltan) { Bien "librerías (pyJianYingDraft, mediapipe, OpenCV, faster-whisper, Pillow)" }
    else { Mal "no cargan: $faltan" "vuelve a lanzar .\instalar.ps1 (paso 2); si usas tu propio Python: pip install -r requirements.txt" }
    Pop-Location
} else { Mal "Python del editor" "lanza .\instalar.ps1: crea .venv con todo dentro" }

# 3. Piezas que se descargan
if (Hay (Join-Path $REPO "vendor\VectCutAPI\pyJianYingDraft")) { Bien "VectCutAPI (escribe los proyectos de CapCut)" } else { Mal "VectCutAPI en vendor\VectCutAPI" "lanza .\instalar.ps1 (paso 3)" }
if (Hay (Join-Path $REPO "modelos\selfie_segmenter.tflite")) { Bien "modelo de recorte de silueta" } else { Mal "modelos\selfie_segmenter.tflite" "lanza .\instalar.ps1 (paso 4)" }
if (Hay (Join-Path $REPO "modelos\hand_landmarker.task")) { Bien "modelo de manos" } else { Ojo "modelos\hand_landmarker.task (solo para detectar gestos)" "lanza .\instalar.ps1 (paso 4)" }
foreach ($f in @("Anton-Regular.ttf", "BebasNeue-Regular.ttf")) {
    if (Hay (Join-Path $REPO "fuentes\$f")) { Bien "fuente $f" } else { Mal "fuentes\$f" "lanza .\instalar.ps1 (paso 5)" }
}

# 4. Tu configuración y tu estilo
$cfgF = Join-Path $REPO "config.json"
if (Hay $cfgF) {
    $cfg = $null
    try { $cfg = Get-Content -Raw -Encoding UTF8 $cfgF | ConvertFrom-Json; Bien "config.json" } catch { Mal "config.json no se puede leer" "revisa comas y comillas; en las rutas usa / en vez de \" }
    if ($cfg) {
        $cap = [Environment]::ExpandEnvironmentVariables($(if ($cfg.carpeta_capcut) { $cfg.carpeta_capcut } else { "%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft" }))
        $pla = if ($cfg.plantilla_capcut) { $cfg.plantilla_capcut } else { "PLANTILLA-REELS" }
        if (Hay $cap) { Bien "carpeta de proyectos de CapCut" } else { Mal "carpeta de proyectos de CapCut ($cap)" "instala CapCut y ábrelo una vez; si tus proyectos están en otro sitio, cámbialo en config.json (carpeta_capcut)" }
        $pp = Join-Path $cap $pla
        if ((Hay (Join-Path $pp "draft_content.json")) -or (Hay (Join-Path $pp "draft_info.json"))) { Bien "plantilla de CapCut '$pla'" }
        else { Mal "plantilla de CapCut '$pla'" "abre CapCut, crea un proyecto vacío, llámalo $pla y cierra CapCut" }
    }
} else { Mal "config.json" "lanza .\instalar.ps1 (paso 6) o copia config.ejemplo.json a config.json" }
$apps = Join-Path $env:LOCALAPPDATA "CapCut\Apps"
if (Hay $apps) {
    $ver = Get-ChildItem $apps -Directory | Where-Object { $_.Name -match '^\d+\.' } | Sort-Object { [version]($_.Name -replace '[^\d.].*$', '') } | Select-Object -Last 1
    if ($ver) {
        if ([int]($ver.Name.Split('.')[0]) -ge 10) { Ojo "CapCut $($ver.Name): la versión 10 o superior puede rechazar los proyectos" "usa CapCut 9.x y desactiva las actualizaciones automáticas" }
        else { Bien "CapCut $($ver.Name)" }
    }
} else { Ojo "no encuentro CapCut instalado en $apps" "instala CapCut 9.x de su web" }
foreach ($f in @("recursos.md", "estilo.md")) {
    if (Hay (Join-Path $REPO "mi-estilo\$f")) { Bien "mi-estilo\$f" } else { Mal "mi-estilo\$f" "lanza .\instalar.ps1 (paso 6): copia el de ejemplo" }
}

# 5. Lo que usa Claude Code
if (Hay (Join-Path $HOME ".claude\skills\montar-reels\SKILL.md")) { Bien "skill montar-reels" } else { Mal "skill montar-reels" "lanza .\instalar.ps1 (paso 7)" }
foreach ($a in @("director-montaje", "revisor-montaje")) {
    if (Hay (Join-Path $HOME ".claude\agents\$a.md")) { Bien "agente $a" } else { Mal "agente $a" "lanza .\instalar.ps1 (paso 7)" }
}

# 6. Control positivo: un borrador de CapCut en memoria con lo que usan los recursos (máscara, texto, capa)
if ((Hay $PY) -and (Hay (Join-Path $REPO "vendor\VectCutAPI\pyJianYingDraft"))) {
    Push-Location (Join-Path $REPO "scripts")
    $r = & $PY -c "import config, json, pyJianYingDraft as d; from pyJianYingDraft import trange; s=d.Script_file(1080,1920); s.add_track(d.Track_type.text,'t'); s.add_track(d.Track_type.video,'v'); x=d.Text_segment('PRUEBA',trange('0s','1s')); x.add_animation(d.CapCut_Text_intro.Blur,'0.25s'); s.add_segment(x,'t'); j=json.loads(s.dumps()); print('ok' if j['tracks'] else 'vacio')" 2>$null
    Pop-Location
    if ($r -eq "ok") { Bien "control: se puede escribir un proyecto de CapCut con textos y animaciones" } else { Mal "control: no se pudo armar un proyecto de prueba" "vuelve a lanzar .\instalar.ps1 y mira el error del paso 8" }
}

Write-Host ""
if ($fallos -eq 0) { Write-Host "Todo listo ($avisos avisos). Abre Claude Code y dile: 'edita este reel' con la ruta de tu vídeo." -ForegroundColor Green }
else { Write-Host "Faltan $fallos cosas (y $avisos avisos). Arréglalas siguiendo las flechas y vuelve a lanzar .\comprobar.ps1." -ForegroundColor Red; exit 1 }
