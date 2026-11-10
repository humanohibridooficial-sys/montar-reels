# python -m unittest discover tests   (desde la raíz del repo)
import os, sys, unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import revisar_entrega as r


def frase(texto, ini=0.5, dur=0.3, hueco=0.05, huecos=None):
    """Palabras con tiempos: huecos = {índice: segundos de silencio ANTES de esa palabra}."""
    out, t = [], ini
    for i, w in enumerate(texto.split()):
        t += (huecos or {}).get(i, 0)
        out.append({"word": " " + w, "start": t, "end": t + dur})
        t += dur + hueco
    return out


PROBLEMA = "minuto setenta y ya no llega a ese balón y alguien te dice que es de cabeza otra vez"


class Arranque(unittest.TestCase):
    def test_repetido(self):
        f = r.arranque(frase("al minuto al minuto setenta y ya no llega"))
        self.assertEqual(f[0][0], "repetir")

    def test_limpio(self):
        self.assertEqual(r.arranque(frase("al minuto setenta y ya no llega")), [])

    def test_no_es_el_del_guion(self):  # caso real de la toma 82
        f = r.arranque(frase("futbolista a minuto 60 miras a la banda"), "futbolista, minuto 60, miras a".split())
        self.assertEqual(f[0][0], "repetir")
        self.assertIn("a minuto", f[0][2])

    def test_coincide_con_el_guion(self):
        self.assertEqual(r.arranque(frase("futbolista minuto 60 miras a la banda"),
                                    r.palabras_de_guion("# nota\n[RÁPIDO] Futbolista, minuto 60, miras a la banda")), [])

    def test_sin_margen(self):
        self.assertEqual(r.arranque(frase("al minuto setenta", ini=0.02))[0][0], "aviso")


class Giro(unittest.TestCase):
    def test_necesitas_gana_a_si_quieres(self):
        p = frase(PROBLEMA + " necesitas a alguien que le prepare si quieres que aguante sígueme")
        self.assertEqual(r.norm(p[r.giro(p)]["word"]), "necesitas")

    def test_si_quieres_solo_si_no_hay_otro(self):
        p = frase(PROBLEMA + " si quieres que aguante sígueme")
        self.assertEqual(r.norm(p[r.giro(p)]["word"]), "si")

    def test_sin_giro(self):
        f, g = r.pausa_y_frenada(frase(PROBLEMA))
        self.assertIsNone(g)
        self.assertEqual(f[0][0], "aviso")


class Pausa(unittest.TestCase):
    def texto(self, pausa):
        n = len(PROBLEMA.split())
        return frase(PROBLEMA + " necesitas a alguien que le prepare", huecos={n: pausa})

    def test_sin_pausa_repite(self):
        f, g = r.pausa_y_frenada(self.texto(0.0))
        self.assertTrue(any(x[0] == "repetir" for x in f))

    def test_con_pausa_vale(self):
        f, g = r.pausa_y_frenada(self.texto(0.8))
        self.assertFalse(any(x[0] == "repetir" for x in f))
        self.assertGreaterEqual(g["pausa_s"], 0.8)

    def test_silencio_en_el_audio_aunque_whisper_pegue_las_palabras(self):
        # Whisper da 0 s entre palabras, pero el audio tiene 0,6 s de silencio antes del giro (como la toma 89)
        p = self.texto(0.0)
        i = r.giro(p)
        db = np.zeros(int((p[-1]["end"] + 1) / .02))
        a = int((p[i]["start"] - 0.6) / .02)
        db[a:int(p[i]["start"] / .02)] = -35
        f, g = r.pausa_y_frenada(p, db)
        self.assertFalse(any(x[0] == "repetir" for x in f))
        self.assertAlmostEqual(g["pausa_s"], 0.6, delta=0.05)

    def test_silencio_antes_cuenta_solo_el_tramo_seguido(self):
        db = np.zeros(200)
        db[50:60] = -30   # 0,2 s
        db[70:75] = -30   # 0,1 s
        self.assertAlmostEqual(r.silencio_antes(db, 75 * .02), 0.2, delta=0.001)


class Frenada(unittest.TestCase):
    def test_solucion_mas_rapida_avisa(self):
        p = frase(PROBLEMA, dur=0.4) + frase("necesitas a alguien que le prepare", ini=8, dur=0.2)
        f, g = r.pausa_y_frenada(p)
        self.assertGreater(g["vel_solucion"], 1)
        self.assertTrue(any("DESPACIO" in x[2] for x in f))


class Final(unittest.TestCase):
    def test_cta_que_se_apaga_repite(self):
        seg = {"start": 0.0, "end": 2.0, "words": frase("si quieres que aguante sígueme", ini=0, dur=0.35)}
        db = np.full(120, -10.0)
        lw = seg["words"][-1]
        db[int(lw["start"] / .02):int(lw["end"] / .02)] = -15  # 5 dB más bajo
        f, c = r.caidas_final([seg], db)
        self.assertEqual(f[0][0], "repetir")

    def test_cta_que_se_oye_vale(self):
        seg = {"start": 0.0, "end": 2.0, "words": frase("si quieres que aguante sígueme", ini=0, dur=0.35)}
        f, c = r.caidas_final([seg], np.full(120, -10.0))
        self.assertEqual(f, [])


class Veredicto(unittest.TestCase):
    def test_orden(self):
        self.assertEqual(r.veredicto([]), "VALE")
        self.assertEqual(r.veredicto([("aviso", None, "x")]), "VALE CON AVISOS")
        self.assertEqual(r.veredicto([("aviso", None, "x"), ("repetir", 1, "y")]), "REPETIR")


if __name__ == "__main__":
    unittest.main()
