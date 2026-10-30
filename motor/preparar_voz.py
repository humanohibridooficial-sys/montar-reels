# Voz limpia (DeepFilterNet) de las tomas del lote de trial reels, en un solo proceso: el modelo se carga una vez.
# Uso: <python del venv df> preparar_voz.py     (salta las que ya tienen voz/<n>-limpio.wav)
import subprocess, pathlib, warnings
warnings.filterwarnings('ignore')
from df.enhance import enhance, init_df, load_audio, save_audio
from tomas import TOMAS, ruta

from rutas import VOZ
model, state, _ = init_df()
for n in TOMAS:
    orig, limpio = VOZ / f'{n}-orig.wav', VOZ / f'{n}-limpio.wav'
    if limpio.exists():
        continue
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(ruta(n)), '-vn', '-ac', '1', '-ar', '48000', '-c:a', 'pcm_s16le', str(orig)], check=True)
    audio, _ = load_audio(str(orig), sr=state.sr())
    save_audio(str(limpio), enhance(model, state, audio), state.sr())
    print('ok', n, flush=True)
