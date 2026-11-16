# python -m unittest discover tests   (desde la raíz del repo)
# Puerta del plan con la pizarra táctica y el crono (16-11): un plan.json mínimo en una carpeta temporal, sin render.
import json, os, pathlib, subprocess, sys, tempfile, unittest

MOTOR = pathlib.Path(__file__).resolve().parent.parent / 'motor'


def plan_base(extras, spans=()):
    """Plan que pasa la puerta: gancho en 0 y un cambio cada 2 s."""
    return {'zoom': [[t, 1.0 + 0.1 * (k % 2)] for k, t in enumerate(range(0, 10, 2))], 'spans': [list(s) for s in spans],
            'panel': [], 'tops': [[0, 1.5, 'Tu hijo', 'en el 70', False]], 'leaks': [], 'byn': None, 'num': None,
            'tachado': None, 'follow': [9.0, 9.5], 'claves': [], 'extras': extras, 'pack': [], 'brollIA': [],
            'subsTop': 1040, 'tarjetas': []}


# Cajas que saca montar.py con jugador [540, 1080] y zona [830, 1100, 140, 45] (la roja cabe debajo de la zona).
PIZARRA = {'tipo': 'pizarra', 'in': 3.0, 'out': 6.0, 'items': [], 'tactica': True, 'tapaSubs': True,
           'cajas': [['círculo', 469, 1009, 611, 1151], ['zona', 687, 1052, 973, 1148], ['flecha', 586, 1065, 834, 1164],
                     ['etiqueta "TU HIJO"', 433, 948, 648, 996], ['etiqueta "AQUÍ YA NO LLEGA"', 553, 1157, 1015, 1215]],
           'fondo': ['p1', 2.5, 7.0]}
CRONO = {'tipo': 'crono', 'in': 2.0, 'out': 6.0, 'items': [], 'desde': 3600, 'hasta': 4200, 'para': 4.5, 'salida': 639,
         'cajas': [['marcador', 70, 300, 579, 374], ['barra', 70, 388, 579, 398], ['aviso "YA NO LLEGA"', 70, 410, 379, 458]]}


def puerta(plan):
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        (d / 'render/ppt/assets').mkdir(parents=True)
        (d / 'datos').mkdir()
        (d / 'render/ppt/plan.json').write_text(json.dumps(plan, ensure_ascii=False), encoding='utf-8')
        (d / 'render/ppt/assets/voice.words.json').write_text(json.dumps({'duration': 10.0, 'words': []}), encoding='utf-8')
        cfg = {k: str(d / v) for k, v in [('carpeta_contenido', 'c'), ('carpeta_tomas', 'c'), ('carpeta_reutilizables', 'c'),
                                          ('carpeta_datos', 'datos'), ('carpeta_render', 'render'), ('carpeta_salida', 'c'), ('om', 'om')]}
        (d / 'config.json').write_text(json.dumps(cfg), encoding='utf-8')
        r = subprocess.run([sys.executable, str(MOTOR / 'puerta_plan.py'), 'pt'], capture_output=True, text=True, encoding='utf-8',
                           env={**os.environ, 'MOTOR_CONFIG': str(d / 'config.json'), 'PYTHONIOENCODING': 'utf-8'}, cwd=MOTOR)
        return r.returncode, r.stdout + r.stderr


def con(base, **cambios):
    return json.loads(json.dumps({**base, **cambios}))


class Pizarra(unittest.TestCase):
    def test_dentro_de_la_zona_segura_pasa(self):
        code, out = puerta(plan_base([PIZARRA], spans=[['p1', 2.5, 7.0, '']]))
        self.assertEqual(code, 0, out)

    def test_etiqueta_bajo_y_1248_falla(self):   # la caja roja donde la ponía la maqueta (top 1235) baja hasta 1293
        cajas = PIZARRA['cajas'][:4] + [['etiqueta "AQUÍ YA NO LLEGA"', 553, 1235, 1015, 1293]]
        code, out = puerta(plan_base([con(PIZARRA, cajas=cajas)], spans=[['p1', 2.5, 7.0, '']]))
        self.assertEqual(code, 1, out)
        self.assertIn('pizarra, etiqueta "AQUÍ YA NO LLEGA" (553,1235-1015,1293) se sale de la zona segura', out)

    def test_etiqueta_sobre_el_jugador_falla(self):   # con la zona en y 1150 la roja no cabe debajo y sube sobre el círculo
        cajas = PIZARRA['cajas'][:4] + [['etiqueta "AQUÍ YA NO LLEGA"', 553, 1035, 1015, 1093]]
        code, out = puerta(plan_base([con(PIZARRA, cajas=cajas)], spans=[['p1', 2.5, 7.0, '']]))
        self.assertEqual(code, 1, out)
        self.assertIn('pisa el círculo del jugador', out)

    def test_zona_pegada_al_borde_derecho_falla(self):
        cajas = PIZARRA['cajas'][:1] + [['zona', 897, 1102, 1043, 1198]] + PIZARRA['cajas'][2:]
        code, out = puerta(plan_base([con(PIZARRA, cajas=cajas)], spans=[['p1', 2.5, 7.0, '']]))
        self.assertEqual(code, 1, out)
        self.assertIn('pizarra, zona', out)

    def test_b_roll_que_se_va_antes_falla(self):
        code, out = puerta(plan_base([con(PIZARRA, fondo=['p1', 2.5, 5.0])], spans=[['p1', 2.5, 5.0, '']]))
        self.assertEqual(code, 1, out)
        self.assertIn('se lleva la imagen congelada', out)


class Crono(unittest.TestCase):
    def test_arriba_a_la_izquierda_pasa(self):
        code, out = puerta(plan_base([CRONO]))
        self.assertEqual(code, 0, out)

    def test_aviso_bajo_y_470_falla(self):   # el aviso donde lo ponía la maqueta (top 430) baja hasta 498, sobre la cabeza
        cajas = CRONO['cajas'][:2] + [['aviso "YA NO LLEGA"', 70, 430, 379, 498]]
        code, out = puerta(plan_base([con(CRONO, cajas=cajas)]))
        self.assertEqual(code, 1, out)
        self.assertIn('crono, aviso "YA NO LLEGA" (70,430-379,498) se sale de su sitio', out)

    def test_mas_ancho_de_600_falla(self):
        cajas = [['marcador', 70, 300, 640, 374]] + CRONO['cajas'][1:]
        code, out = puerta(plan_base([con(CRONO, cajas=cajas)]))
        self.assertEqual(code, 1, out)
        self.assertIn('crono, marcador', out)

    def test_reloj_que_no_llega_a_correr_falla(self):
        code, out = puerta(plan_base([con(CRONO, para=2.4)]))
        self.assertEqual(code, 1, out)
        self.assertIn('el crono se para en 2.4 s', out)

    def test_se_pisa_con_el_titular(self):
        code, out = puerta(plan_base([con(CRONO, **{'in': 1.0})]))
        self.assertEqual(code, 1, out)
        self.assertIn('el crono se pisa con el titular', out)


if __name__ == '__main__':
    unittest.main()
