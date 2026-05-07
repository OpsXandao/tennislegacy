import json
import os

from src.dados import (
    SAVES_DIR,
    get_caminho_jogador_save,
    get_caminho_ranking_save,
    get_caminho_torneio_save,
    validar_nome_save,
)
from src.nome_utils import normalizar_nome
from src.json_utils import salvar_json_seguro
from src.log_jogo import log_erro


def criar_pasta_save(nome_save):
    nome_save = validar_nome_save(nome_save)
    caminho = os.path.join(SAVES_DIR, nome_save)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def salvar_jogo(nome_save: str, jogador_inst):
    """Salva os dados do jogador e atualiza sua entrada no ranking do save."""
    try:
        # 1. Preparar dados para salvar
        if hasattr(jogador_inst, "to_dict"):
            dados = jogador_inst.to_dict()
        else:
            raise ValueError(
                f"Tipo de objeto jogador inválido: {type(jogador_inst)}. Utilize Jogador.from_dict primeiro."
            )

        # 2. Salvar o arquivo jogador.json
        criar_pasta_save(nome_save)
        jogador_path = get_caminho_jogador_save(nome_save)
        salvar_json_seguro(jogador_path, dados)

        # 3. Atualizar o ranking local do save
        atualizar_jogador_no_ranking(nome_save, dados)

    except Exception as e:
        log_erro(nome_save, "salvar_jogo", e)


def atualizar_jogador_no_ranking(nome_save: str, dados_jogador: dict):
    """Atualiza as estatísticas do jogador humano no arquivo de ranking do save."""
    genero = dados_jogador.get("genero", "masculino")
    ranking_path = get_caminho_ranking_save(nome_save, genero=genero)

    if not os.path.exists(ranking_path):
        return

    try:
        from src.ranking import SistemaRanking

        rk_obj = SistemaRanking(ranking_path)
        nome_norm = normalizar_nome(dados_jogador.get("nome", ""))

        # Busca o jogador no ranking (rk_obj.buscar_jogador_por_nome já lida com cache e normalização)
        j = rk_obj.buscar_jogador_por_nome(nome_norm)

        if j:
            # Campos que devem ser sincronizados com o ranking
            campos_sync = [
                "idade",
                "xp",
                "nivel",
                "energia",
                "ritmo_jogo",
                "moral",
                "dinheiro",
                "atributos",
                "atributos_psicologicos",
                "fadiga",
                "status_lesao",
                "status_doenca",
                "pontos_de_skill",
                "pontos_ytd",
                "historico_torneios",
                "transacoes",
            ]
            for campo in campos_sync:
                if campo in dados_jogador:
                    j[campo] = dados_jogador[campo]

            from src.player_ratings import ajustar_atributo_duplas, calcular_overall_contextual

            ajustar_atributo_duplas(j)
            j["overall"] = calcular_overall_contextual(j)

            # Salva usando a lógica de sharding (índice lean + arquivo individual)
            rk_obj.ordenar(recalculate=True)
            rk_obj.salvar_ranking()

    except Exception as e:
        log_erro(nome_save, "atualizar_jogador_no_ranking", e)


def tirar_snapshot_carreira(jogador, ano=None):
    """Salva um snapshot dos atributos do jogador para histórico de progressão."""
    snapshot = {
        "ano": int(ano if ano is not None else getattr(jogador, "ano", 2026)),
        "semana": jogador.semana,
        "nivel": jogador.nivel,
        "overall": jogador.calcular_overall(),
        "atributos": jogador.atributos.copy(),
    }

    # Evita duplicatas na mesma semana e ano
    if (
        not jogador.snapshots_carreira
        or (jogador.snapshots_carreira[-1]["semana"], jogador.snapshots_carreira[-1].get("ano")) 
           != (jogador.semana, snapshot["ano"])
    ):
        jogador.snapshots_carreira.append(snapshot)


def salvar_estado_atual_torneio(
    nome_save, fase_atual, confrontos, resultados, jogador_vivo=True
):
    try:
        caminho = get_caminho_torneio_save(nome_save)

        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                estado = json.load(f)
        else:
            estado = {
                "rodadas": {},
                "resultados": {},
                "fase_atual": fase_atual,
                "jogador_vivo": jogador_vivo,
            }

        estado["rodadas"][fase_atual] = [
            (
                a["nome"] if isinstance(a, dict) else a,
                b["nome"] if isinstance(b, dict) else b,
            )
            for a, b in confrontos
        ]

        estado["resultados"][fase_atual] = resultados
        estado["jogador_vivo"] = jogador_vivo
        estado["fase_atual"] = fase_atual

        salvar_json_seguro(caminho, estado)

    except Exception as e:
        log_erro(
            nome_save,
            "salvar_estado_atual_torneio",
            e,
            {"fase_atual": fase_atual, "jogador_vivo": jogador_vivo},
        )


def atualizar_estado_jogador(caminho, vivo=True, fase_finalizada=False):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            estado = json.load(f)
        estado["jogador_vivo"] = vivo
        if fase_finalizada:
            estado["fase_atual"] = "finalizado"
        salvar_json_seguro(caminho, estado)
    except Exception as e:
        log_erro(
            None,
            "atualizar_estado_jogador",
            e,
            {"caminho": caminho, "vivo": vivo, "fase_finalizada": fase_finalizada},
        )
