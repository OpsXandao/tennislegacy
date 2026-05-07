from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from websockets import connect as ws_connect

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "db"
SAVES_DIR = ROOT / "saves"
HOST = "127.0.0.1"
PORT = 8011
BASE_URL = f"http://{HOST}:{PORT}"


@dataclass
class Response:
    status: int
    data: Any
    text: str


@dataclass
class StepResult:
    label: str
    ok: bool
    status: int | str
    detail: str


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.results: list[StepResult] = []

    def _request(self, method: str, path: str, payload: Any | None = None) -> Response:
        url = f"{self.base_url}{path}"
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, method=method, headers=headers, data=body)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                text = resp.read().decode("utf-8")
                data = json.loads(text) if text else None
                return Response(resp.getcode(), data, text)
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8")
            try:
                data = json.loads(text) if text else None
            except json.JSONDecodeError:
                data = text
            return Response(exc.code, data, text)

    def expect(
        self,
        label: str,
        method: str,
        path: str,
        payload: Any | None = None,
        allowed_statuses: set[int] | None = None,
    ) -> Response:
        allowed = allowed_statuses or {200}
        resp = self._request(method, path, payload)
        ok = resp.status in allowed
        detail = ""
        if not ok:
            detail = resp.text[:400]
        self.results.append(
            StepResult(label=label, ok=ok, status=resp.status, detail=detail)
        )
        status_text = "OK" if ok else "FAIL"
        print(f"[{status_text}] {label} -> {resp.status}")
        if detail:
            print(detail)
        if not ok:
            raise RuntimeError(f"Falha em {label}: status {resp.status}")
        return resp


def file_manifest(base_dir: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(base_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest[rel] = digest
    return manifest


def wait_for_server(client: ApiClient, timeout_s: float = 30.0) -> None:
    started = time.time()
    while time.time() - started < timeout_s:
        try:
            resp = client._request("GET", "/")
            if resp.status == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("API não ficou pronta a tempo.")


def start_server() -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def stop_server(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


def unique_save_name(suffix: str) -> str:
    return f"smoke_{suffix}_{int(time.time() * 1000)}"


def save_player_path(save_name: str) -> Path:
    return SAVES_DIR / save_name / "jogador.json"


def save_ranking_path(save_name: str, gender: str = "atp") -> Path:
    filename = "ranking_atp.json" if gender == "atp" else "ranking_wta.json"
    return SAVES_DIR / save_name / filename


def save_copied_rankings_exist(save_name: str) -> None:
    expected = [
        "ranking_atp.json",
        "ranking_wta.json",
        "ranking_atp_duplas.json",
        "ranking_wta_duplas.json",
    ]
    missing = [name for name in expected if not (SAVES_DIR / save_name / name).exists()]
    if missing:
        raise RuntimeError(
            f"Save {save_name} não copiou arquivos-base esperados: {missing}"
        )


def patch_player_json(save_name: str, mutator) -> None:
    path = save_player_path(save_name)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def patch_ranking_player_points(save_name: str, player_name: str, points: int) -> None:
    path = save_ranking_path(save_name, "atp")
    ranking = json.loads(path.read_text(encoding="utf-8"))
    target_norm = player_name.casefold()
    updated = False
    for item in ranking:
        if str(item.get("nome", "")).casefold() == target_norm:
            item["pontos"] = points
            item["pontos_ytd"] = points
            updated = True
            break
    if not updated:
        raise RuntimeError(f"Jogador {player_name} não encontrado em {path}")
    path.write_text(json.dumps(ranking, ensure_ascii=False, indent=2), encoding="utf-8")


def create_regular_tournament(client: ApiClient, save_name: str) -> str:
    client.expect(
        f"{save_name}: carregar", "POST", "/api/save/carregar", {"nome": save_name}
    )
    atual = client.expect(
        f"{save_name}: calendario atual", "GET", "/api/calendario/atual"
    ).data
    torneios = atual.get("torneios", [])
    escolhido = next(
        (
            t
            for t in torneios
            if t.get("tipo") not in {"Davis Cup", "Billie Jean King Cup", "United Cup"}
        ),
        None,
    )
    if not escolhido:
        raise RuntimeError("Nenhum torneio regular disponível para smoke test.")
    nome = escolhido["nome"]
    client.expect(
        f"{save_name}: historico torneio",
        "GET",
        f"/api/torneio/historico?nome={urllib.parse.quote(nome)}",
    )
    client.expect(
        f"{save_name}: criar torneio",
        "POST",
        "/api/torneio/criar",
        {"modalidade": "simples", "torneio_nome": nome},
    )
    return nome


async def exercise_websocket(partida_id: str) -> None:
    uri = f"ws://{HOST}:{PORT}/ws/partida/{partida_id}"
    async with ws_connect(uri) as websocket:
        msg1 = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
        if not isinstance(msg1, dict):
            raise RuntimeError("Primeira mensagem do websocket inválida.")
        await websocket.send(json.dumps({"acao": "pausar"}))
        await asyncio.sleep(0.2)
        await websocket.send(json.dumps({"acao": "continuar"}))
        msg2 = json.loads(await asyncio.wait_for(websocket.recv(), timeout=10))
        if not isinstance(msg2, dict):
            raise RuntimeError("Segunda mensagem do websocket inválida.")


def cleanup_save_dir(save_name: str) -> None:
    path = SAVES_DIR / save_name
    if path.exists():
        shutil.rmtree(path)


def advance_until_davis(
    client: ApiClient, save_name: str, max_steps: int = 60
) -> dict[str, Any]:
    client.expect(
        f"{save_name}: carregar", "POST", "/api/save/carregar", {"nome": save_name}
    )
    for step in range(max_steps):
        resp = client.expect(
            f"{save_name}: checar convocacao semana {step + 1}",
            "GET",
            "/api/torneio/checar-convocacao",
        ).data
        torneio = resp.get("torneio")
        if torneio:
            if not resp.get("convocado"):
                raise RuntimeError(
                    f"Davis encontrada, mas jogador não convocado: {resp.get('mensagem')}"
                )
            return torneio
        client.expect(
            f"{save_name}: avancar semana {step + 1}", "POST", "/api/calendario/avancar"
        )
    raise RuntimeError("Não encontrei semana de Davis no limite configurado.")


def main() -> int:
    original_db_manifest = file_manifest(DB_DIR)
    client = ApiClient(BASE_URL)
    proc = start_server()
    created_saves: list[str] = []
    try:
        wait_for_server(client)

        client.expect("root", "GET", "/")
        client.expect("sessao inicial", "GET", "/api/sessao")
        client.expect("save arquetipos", "GET", "/api/save/arquetipos")
        client.expect("save nacionalidades", "GET", "/api/save/nacionalidades")
        client.expect("listar saves", "GET", "/api/saves")
        client.expect(
            "logs frontend",
            "POST",
            "/api/logs/frontend",
            {
                "kind": "smoke_test",
                "message": "smoke test route coverage",
                "stack": None,
                "url": "http://smoke.test/",
                "user_agent": "smoke-test",
                "component_stack": None,
                "extra": {"suite": "all_routes"},
            },
        )

        base_save = unique_save_name("base")
        created_saves.append(base_save)
        client.expect(
            "criar save base",
            "POST",
            "/api/save/criar",
            {
                "nome": base_save,
                "nome_jogador": "Smoke Tester",
                "nacionalidade": "[BR] Brasil",
                "tour": "atp",
                "idade": 18,
                "archetype_id": "3",
                "mental_id": "5",
            },
        )
        save_copied_rankings_exist(base_save)
        client.expect("preview save base", "GET", f"/api/save/{base_save}/preview")
        client.expect(
            "carregar save base", "POST", "/api/save/carregar", {"nome": base_save}
        )
        client.expect("sessao carregada", "GET", "/api/sessao")
        client.expect("jogador", "GET", "/api/jogador")
        client.expect("jogador atributos", "GET", "/api/jogador/atributos")
        client.expect("jogador equipe", "GET", "/api/jogador/equipe")
        client.expect("jogador patrocinios", "GET", "/api/jogador/patrocinios")
        client.expect("jogador financeiro", "GET", "/api/jogador/financeiro")
        client.expect(
            "jogador historico partidas", "GET", "/api/jogador/historico-partidas"
        )
        client.expect(
            "jogador ranking detalhado", "GET", "/api/jogador/ranking-detalhado"
        )
        client.expect("jogador carreira", "GET", "/api/jogador/carreira")
        client.expect("ranking atp", "GET", "/api/ranking/atp?limit=25&offset=0")
        client.expect("ranking wta", "GET", "/api/ranking/wta?limit=25&offset=0")
        client.expect(
            "ranking duplas atp", "GET", "/api/ranking/duplas/atp?limit=25&offset=0"
        )
        client.expect(
            "ranking duplas wta", "GET", "/api/ranking/duplas/wta?limit=25&offset=0"
        )
        client.expect(
            "ranking nacoes davis", "GET", "/api/ranking/nacoes/davis?limit=10&offset=0"
        )
        client.expect(
            "ranking nacoes legacy", "GET", "/api/ranking/nacoes?limit=10&offset=0"
        )
        client.expect("calendario atual", "GET", "/api/calendario/atual")
        client.expect("calendario atual wta", "GET", "/api/calendario/atual?tour=wta")
        client.expect("calendario semana 1", "GET", "/api/calendario/semana/1")
        client.expect(
            "calendario semana 1 wta", "GET", "/api/calendario/semana/1?tour=wta"
        )
        client.expect("mundo proximos", "GET", "/api/mundo/proximos")
        client.expect("mundo noticias", "GET", "/api/mundo/noticias")
        client.expect("mundo ao vivo", "GET", "/api/mundo/ao-vivo")
        client.expect("mundo race to finals", "GET", "/api/mundo/race-to-finals")
        client.expect("torneio estado vazio", "GET", "/api/torneio/estado")
        client.expect(
            "torneio checar convocacao", "GET", "/api/torneio/checar-convocacao"
        )
        profissionais = client.expect(
            "mercado profissionais", "GET", "/api/mercado/profissionais"
        ).data
        primeiro_empresario = profissionais["empresario"][0]["id"]
        client.expect(
            "mercado contratar",
            "POST",
            "/api/mercado/contratar",
            {"prof_id": primeiro_empresario},
        )
        client.expect(
            "mercado demitir",
            "POST",
            "/api/mercado/demitir",
            {"prof_id": primeiro_empresario},
        )
        client.expect("email inbox vazio", "GET", "/api/email/inbox")
        patch_player_json(
            base_save,
            lambda data: data.update(
                {
                    "caixa_email": [
                        {
                            "id": "smoke-email-1",
                            "tipo": "teste",
                            "assunto": "Smoke",
                            "status": "pendente",
                        }
                    ]
                }
            ),
        )
        client.expect(
            "recarregar save com email",
            "POST",
            "/api/save/carregar",
            {"nome": base_save},
        )
        client.expect("email inbox populado", "GET", "/api/email/inbox")
        client.expect(
            "email acao deletar",
            "POST",
            "/api/email/acao",
            {"email_id": "smoke-email-1", "acao": "deletar"},
        )
        client.expect("historico goat", "GET", "/api/historico/goat")
        client.expect("historico campeoes", "GET", "/api/historico/campeoes")
        patch_player_json(
            base_save, lambda data: data.__setitem__("pontos_de_skill", 1)
        )
        client.expect(
            "recarregar save com skill point",
            "POST",
            "/api/save/carregar",
            {"nome": base_save},
        )
        progressao = client.expect(
            "progressao status", "GET", "/api/progressao/status"
        ).data
        atributo_tecnico = next(iter(progressao["atributos"].keys()))
        client.expect(
            "progressao alocar",
            "POST",
            "/api/progressao/alocar",
            {"tipo": "tecnico", "atributo": atributo_tecnico},
        )
        client.expect("duplas sugestoes", "GET", "/api/duplas/sugestoes")
        busca_duplas = client.expect(
            "duplas buscar nome", "GET", "/api/duplas/buscar?nome=a"
        ).data
        client.expect(
            "duplas buscar nacionalidade",
            "GET",
            "/api/duplas/buscar?nacionalidade=%5BBR%5D%20Brasil",
        )
        parceiro_nome = busca_duplas["parceiros"][0]["nome"]
        client.expect(
            "duplas convidar",
            "POST",
            "/api/duplas/convidar",
            {"npc_nome": parceiro_nome, "torneio_tipo": "ATP 250"},
        )
        client.expect("treinamento opcoes", "GET", "/api/treinamento/opcoes")
        client.expect(
            "treinamento executar",
            "POST",
            "/api/treinamento/executar",
            {"foco": "tecnico"},
        )
        client.expect("save salvar", "POST", "/api/save/salvar")
        client.expect("treinamento descanso", "POST", "/api/treinamento/descanso")

        tournament_save = unique_save_name("tour")
        created_saves.append(tournament_save)
        client.expect(
            "criar save torneio",
            "POST",
            "/api/save/criar",
            {
                "nome": tournament_save,
                "nome_jogador": "Tournament Tester",
                "nacionalidade": "[BR] Brasil",
                "tour": "atp",
                "idade": 18,
                "archetype_id": "3",
                "mental_id": "5",
            },
        )
        save_copied_rankings_exist(tournament_save)
        tournament_name = create_regular_tournament(client, tournament_save)
        client.expect("torneio estado ativo", "GET", "/api/torneio/estado")
        encoded_tournament_name = urllib.parse.quote(tournament_name)
        client.expect(
            "mundo detalhes torneio",
            "GET",
            f"/api/mundo/torneio/{encoded_tournament_name}?tour=atp",
        )
        client.expect(
            "mundo bracket torneio",
            "GET",
            f"/api/mundo/bracket?torneio={encoded_tournament_name}&tour=atp",
        )
        partida = client.expect(
            "partida iniciar",
            "POST",
            "/api/partida/iniciar",
            {"modo": "estrategista"},
        ).data
        partida_id = partida["partida_id"]
        client.expect(
            "partida estrategia",
            "POST",
            "/api/partida/estrategia",
            {"partida_id": partida_id, "estrategia": "agressivo"},
        )
        client.expect(
            "partida ponto",
            "POST",
            "/api/partida/ponto",
            {"partida_id": partida_id},
        )
        client.expect(
            "partida simular set",
            "POST",
            "/api/partida/simular-set",
            {"partida_id": partida_id},
        )
        client.expect(
            "partida simular partida",
            "POST",
            "/api/partida/simular-partida",
            {"partida_id": partida_id},
        )
        client.expect("torneio avancar fase", "POST", "/api/torneio/avancar-fase")

        desist_save = unique_save_name("desist")
        created_saves.append(desist_save)
        client.expect(
            "criar save desistir",
            "POST",
            "/api/save/criar",
            {
                "nome": desist_save,
                "nome_jogador": "Retire Tester",
                "nacionalidade": "[BR] Brasil",
                "tour": "atp",
                "idade": 18,
                "archetype_id": "3",
                "mental_id": "5",
            },
        )
        create_regular_tournament(client, desist_save)
        client.expect("torneio desistir", "POST", "/api/torneio/desistir")

        ws_save = unique_save_name("ws")
        created_saves.append(ws_save)
        client.expect(
            "criar save ws",
            "POST",
            "/api/save/criar",
            {
                "nome": ws_save,
                "nome_jogador": "Websocket Tester",
                "nacionalidade": "[BR] Brasil",
                "tour": "atp",
                "idade": 18,
                "archetype_id": "3",
                "mental_id": "5",
            },
        )
        create_regular_tournament(client, ws_save)
        partida_ws = client.expect(
            "partida iniciar ws",
            "POST",
            "/api/partida/iniciar",
            {"modo": "estrategista"},
        ).data["partida_id"]
        asyncio.run(exercise_websocket(partida_ws))
        client.results.append(StepResult("websocket partida", True, "WS", ""))
        print("[OK] websocket partida -> WS")

        davis_save = unique_save_name("davis")
        created_saves.append(davis_save)
        client.expect(
            "criar save alexandre",
            "POST",
            "/api/save/criar-alexandre",
            {"nome": davis_save},
        )
        save_copied_rankings_exist(davis_save)
        patch_ranking_player_points(davis_save, "Alexandre Paiva", 5_000_000)
        client.expect(
            "recarregar save davis", "POST", "/api/save/carregar", {"nome": davis_save}
        )
        torneio_davis = advance_until_davis(client, davis_save)
        client.expect(
            "criar torneio davis",
            "POST",
            "/api/torneio/criar",
            {"modalidade": "simples", "torneio_nome": torneio_davis["nome"]},
        )
        client.expect("davis estado", "GET", "/api/davis/estado")
        client.expect("davis proximo", "GET", "/api/davis/proximo")
        client.expect(
            "davis simular atual",
            "POST",
            "/api/davis/simular-atual",
            allowed_statuses={200, 409},
        )

        for save_name in list(created_saves):
            client.expect(
                f"deletar save {save_name}", "DELETE", f"/api/save/{save_name}"
            )
            created_saves.remove(save_name)

        final_db_manifest = file_manifest(DB_DIR)
        if original_db_manifest != final_db_manifest:
            changed = sorted(
                set(original_db_manifest.keys()) | set(final_db_manifest.keys())
            )
            diffs = [
                path
                for path in changed
                if original_db_manifest.get(path) != final_db_manifest.get(path)
            ]
            raise RuntimeError(f"O conteúdo de db/ foi alterado: {diffs}")

        print("\nResumo:")
        print(f"Rotas/cenários validados: {len(client.results)}")
        print("db/ permaneceu inalterado.")
        return 0
    except Exception as exc:
        print(f"\nERRO: {exc}")
        if proc.stdout:
            try:
                output = proc.stdout.read()
                if output:
                    print("\n--- Saída do servidor ---")
                    print(output[-8000:])
            except Exception:
                pass
        return 1
    finally:
        stop_server(proc)
        for save_name in created_saves:
            cleanup_save_dir(save_name)


if __name__ == "__main__":
    raise SystemExit(main())
