import urllib.request
import json
import time

BASE_URL = "http://localhost:8002"


def test_route(method, path, data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
        json_data = json.dumps(data).encode("utf-8")
    else:
        json_data = None

    try:
        with urllib.request.urlopen(req, data=json_data) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            print(f"[{status}] {method} {path} -> OK")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"[{e.code}] {method} {path} -> FAILED: {body}")
        return None
    except Exception as e:
        print(f"[ERR] {method} {path} -> ERROR: {e}")
        return None


def run_tests():
    print("Starting API tests...")

    # 1. Root
    test_route("GET", "/")

    # 2. Carregar Save
    test_route("POST", "/api/save/carregar", {"nome": "test_api_save"})

    # 3. Jogador
    test_route("GET", "/api/jogador")
    test_route("GET", "/api/jogador/atributos")

    # 4. Calendario
    test_route("GET", "/api/calendario/atual")
    test_route("GET", "/api/calendario/semana/1")

    # 5. Ranking
    test_route("GET", "/api/ranking/atp")

    # 6. Mundo
    test_route("GET", "/api/mundo/proximos")
    test_route("GET", "/api/mundo/noticias")

    # 7. Torneio (Estado)
    test_route("GET", "/api/torneio/estado")
    test_route("GET", "/api/torneio/checar-convocacao")

    # 8. Mercado
    test_route("GET", "/api/mercado/profissionais")

    # 9. Email
    test_route("GET", "/api/email/inbox")

    # 10. Historico
    test_route("GET", "/api/historico/goat")

    print("Tests finished.")


if __name__ == "__main__":
    # Wait for uvicorn to start
    time.sleep(2)
    run_tests()
