# Descarga de Wikimedia Commons las fotos originales que usa la plantilla (todas CC0 o dominio público)
# y comprueba la licencia de cada una antes de guardarla. Después: python prep_assets.py originales/
import os
import requests

H = {'User-Agent': 'montar-reels/plantilla-pared-azul'}
FOTOS = {
    'penalti': 'File:Penalty Kick of Daigo Furukawa(FC Osaka)2.jpg',
    'michels': 'File:Nederland tegen Oostenrijk 1-1 bondscoach Fadrhonc en Michels langs de lijn kij, Bestanddeelnr 927-0867.jpg',
    'keeper': 'File:Keeper Rynio duikt naar de bal, Bestanddeelnr 921-7328.jpg',
    'kopbal': 'File:Spelmoment kopbal, Bestanddeelnr 929-0942.jpg',
    'comida': 'File:Feijenoord in Breda in trainingskamp, de spelers aan de maaltijd, linkerkant taf, Bestanddeelnr 914-9140.jpg',
    'masaje': 'File:Training Feyenoord, Coen Moulijn gemasseerd door Gerard Meijer, Bestanddeelnr 918-0454.jpg',
    'carrera': 'File:Man in pelvis cloth running at a half-mile gait (rbm-QP301M8-1887-060).jpg',
}
LIBRES = ('CC0', 'Public domain', 'No restrictions')

os.makedirs('originales', exist_ok=True)
for nombre, titulo in FOTOS.items():
    r = requests.get('https://commons.wikimedia.org/w/api.php', headers=H, timeout=30, params={
        'action': 'query', 'format': 'json', 'titles': titulo, 'prop': 'imageinfo',
        'iiprop': 'url|extmetadata', 'iiurlwidth': 1400}).json()
    pagina = next(iter(r['query']['pages'].values()))
    if 'imageinfo' not in pagina:
        print(f'{nombre}: no encontrada ({titulo})'); continue
    ii = pagina['imageinfo'][0]
    lic = ii['extmetadata'].get('LicenseShortName', {}).get('value', '?')
    if lic not in LIBRES:
        print(f'{nombre}: licencia {lic}, no se descarga'); continue
    with open(f'originales/{nombre}.jpg', 'wb') as f:
        f.write(requests.get(ii['thumburl'], headers=H, timeout=60).content)
    print(f'{nombre}: {lic}')
