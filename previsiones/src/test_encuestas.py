import pathlib, sys, unittest
from datetime import date

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from encuestas import _fin_campo, _muestra, clave  # noqa: E402
import motor  # noqa: E402


class Encuestas(unittest.TestCase):
    def test_fechas_de_campo(self):
        self.assertEqual(_fin_campo('01-08/10/2026', '2026-10-11'), date(2026, 10, 8))
        self.assertEqual(_fin_campo('29/09-01/10/2026', '2026-10-03'), date(2026, 10, 1))
        self.assertEqual(_fin_campo('07/09/2026', '2026-09-13'), date(2026, 9, 7))
        self.assertEqual(_fin_campo(float('nan'), '2019-11-03'), date(2019, 10, 31))

    def test_muestra_y_casa(self):
        self.assertEqual(_muestra('2.173 entrevistas'), 2173)
        self.assertEqual(_muestra('No publicado'), 1000)
        self.assertEqual(_muestra('5.025 entrevistas'), 3000)
        self.assertEqual(clave('Sigma Dos'), clave('SigmaDos'))
        self.assertEqual(clave('SocioMétrica'), clave('Sociométrica'))

    @unittest.skipUnless(motor.BASE2026.exists(), 'falta base2026_secciones.csv')
    def test_ajuste_clava_la_media(self):
        provs, cuotas, validos, indices = motor.base_v1()
        objetivo = {'PP': .31, 'PSOE': .27, 'Vox': .19, 'Sumar': .065, 'Podemos': .03, 'SALF': .017, 'ERC': .023}
        c = motor.ajusta_a_encuestas(cuotas, validos, indices, objetivo)
        nac = (c * validos[:, None]).sum(0) / validos.sum()
        for k, t in objetivo.items():
            self.assertAlmostEqual(nac[motor.LISTAS_V1.index(k)], t, places=4)
        self.assertTrue((c.sum(1) <= 0.985 + 1e-9).all())
        self.assertNotIn('Aliança', motor.LISTAS_V1)   # no se presenta al 29N

    @unittest.skipUnless(motor.EUROPEAS2024.exists(), 'falta europeas2024_secciones.csv')
    def test_vox_en_tenerife(self):
        # en 2023 se anuló su candidatura al Congreso en Santa Cruz de Tenerife: no puede partir de cero en 2026
        provs, cuotas, _, _ = motor.base_v1()
        self.assertGreater(cuotas[provs.index('38'), motor.LISTAS_V1.index('Vox')], 0.03)
        factor, _ = motor.senal_europeas(provs)
        self.assertTrue(all(np.isfinite(f).all() for f in factor.values()))


if __name__ == '__main__':
    unittest.main()
