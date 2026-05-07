import unittest

from api.logging_utils import extract_exception_details, summarize_detail


class ApiLoggingTests(unittest.TestCase):
    def test_summarize_detail_com_dict_prioriza_detail(self):
        resumo = summarize_detail({"detail": "Sessao nao iniciada.", "code": "NO_SESSION"})
        self.assertEqual(resumo, "Sessao nao iniciada.")

    def test_extract_exception_details_identifica_causa_raiz(self):
        try:
            try:
                raise ValueError("ranking corrompido")
            except ValueError as exc:
                raise RuntimeError("falha ao carregar save") from exc
        except RuntimeError as exc_final:
            detalhes = extract_exception_details(exc_final)

        self.assertEqual(detalhes["error_type"], "RuntimeError")
        self.assertEqual(detalhes["root_cause_type"], "ValueError")
        self.assertEqual(detalhes["root_cause"], "ranking corrompido")
        self.assertEqual(len(detalhes["cause_chain"]), 2)
        self.assertIn("RuntimeError: falha ao carregar save", detalhes["traceback"])


if __name__ == "__main__":
    unittest.main()
