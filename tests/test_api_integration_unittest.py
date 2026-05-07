import importlib.util
import unittest


@unittest.skip("httpx nao instalado; testes de integracao HTTP ficam desabilitados neste ambiente.")
class ApiIntegrationTests(unittest.TestCase):
    def test_placeholder(self):
        self.skipTest("Substituir por testes com TestClient quando httpx estiver disponivel.")


if __name__ == "__main__":
    unittest.main()
