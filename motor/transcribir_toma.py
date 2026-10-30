# Palabras de una toma con faster-whisper (large-v3-turbo), en el formato de palabras.json. Lo llama preparar.py
# con el Python de faster-whisper (python_fw):   <python_fw> transcribir_toma.py <toma.mp4>   -> JSON por la salida
# El audio va ya decodificado por ffmpeg: el PyAV de ese entorno es más nuevo de lo que espera faster-whisper
# ("open() got an unexpected keyword argument 'metadata_errors'"). CUDA se prueba de verdad (la transcripción es
# perezosa: si no se recorre, no falla) y si no va, procesador.
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-vn', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.float32)
try:
    m = WhisperModel('large-v3-turbo', device='cuda', compute_type='float16')
    list(m.transcribe(audio[:16000 * 5], language='es')[0])
except Exception:
    m = WhisperModel('large-v3-turbo', device='cpu', compute_type='int8')
segs, _ = m.transcribe(audio, language='es', word_timestamps=True, beam_size=5)
print(json.dumps([{'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip(),
                   'words': [{'word': w.word.strip(), 'start': round(w.start, 2), 'end': round(w.end, 2)} for w in s.words]}
                  for s in segs], ensure_ascii=False))
