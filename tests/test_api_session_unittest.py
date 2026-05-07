import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import api.session as session_mod


class ApiSessionTests(unittest.TestCase):
    def tearDown(self):
        session_mod.clear_sessao()

    def test_refresh_session_recarrega_quando_cache_esta_incompleto(self):
        # Simula um estado de pool inconsistente
        sess = session_mod.Session("save_teste")
        sess._ranking_atp = object()
        sess._ranking_wta = None
        sess._ranking_duplas_atp = object()
        sess._ranking_duplas_wta = object()
        session_mod._sessions_pool["save_teste"] = (sess, time.monotonic())

        with patch.object(sess, "rebuild_rankings") as mock_rebuild:
            session_mod.refresh_session("save_teste")

        self.assertEqual(sess.nome_save_ativo, "save_teste")
        # Note: rebuild_rankings is no longer called by refresh_session directly,
        # but rankings are cleared to be re-built on access.
        self.assertIsNone(sess._ranking_atp)


if __name__ == "__main__":
    unittest.main()
