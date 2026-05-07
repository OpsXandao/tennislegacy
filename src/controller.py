import os
import random

from src.dados import get_caminho_torneio_save, carregar_estado_torneio
from src.interface.menu_principal import menu_principal
from src.interface.menu_torneio import menu_torneio
from src.interface.menu_davis import menu_davis
from src.pontuacao import distribuir_pontos_torneio, distribuir_pontos_davis
from src.imprensa import disparar_entrevista
from src.save import salvar_jogo
from src.progressao import aplicar_melhorias_naturais
from src.log_jogo import log_erro
from src.json_utils import salvar_json_seguro
from src.io_utils import (
    safe_input,
    print_blue,
)
from src.nome_utils import normalizar_nome

FASES_DAVIS_ATIVAS = ("qualifiers", "quartas", "semifinal", "final")
FASES_TORNEIO_ATIVAS = (
    "qualy_1",
    "qualy_2",
    "qualy_r1",
    "qualy_r2",
    "qualy_r3",
    "pre_oitavas",
    "oitavas",
    "r128",
    "r96",
    "r64",
    "r32",
    "r16",
    "quartas",
    "semifinal",
    "final",
)


def _aplicar_progressao_natural_pos_torneio(jogador_inst, nome_save, estado_torneio):
    pendente = estado_torneio.get("progressao_natural_pendente", {})
    if not isinstance(pendente, dict) or not pendente:
        return False

    melhorias = aplicar_melhorias_naturais(jogador_inst, pendente)
    if not melhorias:
        return False

    print_blue("\n📈 Progressão natural aplicada no pós-torneio:")
    for attr, novo_valor in sorted(melhorias.items()):
        print(f"  + {attr}: {novo_valor}")
    salvar_jogo(nome_save, jogador_inst)
    estado_torneio["progressao_natural_pendente"] = {}
    try:
        salvar_json_seguro(
            get_caminho_torneio_save(nome_save, genero=jogador_inst.genero),
            estado_torneio,
        )
    except Exception as e:
        log_erro(
            nome_save,
            "limpar_progressao_natural_pendente",
            e,
            {"genero": getattr(jogador_inst, "genero", "masculino")},
        )
        return False
    return True


def _estado_pertence_ao_jogador(estado, jogador_nome):
    if not isinstance(estado, dict):
        return False
    return normalizar_nome(estado.get("jogador")) == normalizar_nome(jogador_nome)


def _get_estado_finalizacao(estado_torneio):
    finalizacao = estado_torneio.get("finalizacao_controller", {})
    if not isinstance(finalizacao, dict):
        finalizacao = {}
        estado_torneio["finalizacao_controller"] = finalizacao
    return finalizacao


def _salvar_estado_torneio(nome_save, genero, estado_torneio):
    salvar_json_seguro(
        get_caminho_torneio_save(nome_save, genero=genero), estado_torneio
    )


def _marcar_finalizacao_torneio(nome_save, genero, estado_torneio, chave):
    finalizacao = _get_estado_finalizacao(estado_torneio)
    finalizacao[chave] = True
    _salvar_estado_torneio(nome_save, genero, estado_torneio)


def _executar_etapa_finalizacao(
    nome_save, genero, estado_torneio, finalizacao, chave, acao
):
    if finalizacao.get(chave):
        return False
    acao()
    _marcar_finalizacao_torneio(nome_save, genero, estado_torneio, chave)
    return True


def _recarregar_jogador_pos_semana(
    jogador_inst,
    nome_save,
    fase=None,
    contexto_log="recarregar_jogador_pos_avanco_semana",
):
    from src.jogador import carregar_jogador

    jogador_recarregado = carregar_jogador(nome_save)
    if jogador_recarregado is not None:
        return jogador_recarregado

    log_erro(
        nome_save,
        contexto_log,
        RuntimeError("carregar_jogador retornou None"),
        {"fase": fase},
    )
    return jogador_inst


def _remover_arquivo_torneio(caminho_torneio, nome_save, fase, contexto_log):
    try:
        os.remove(caminho_torneio)
        return True
    except OSError as e:
        print(f"❌ Erro ao remover o arquivo do torneio: {e}")
        log_erro(
            nome_save,
            contexto_log,
            e,
            {"caminho_torneio": caminho_torneio, "fase": fase},
        )
        return False


def _fase_davis_ativa(fase):
    return fase in FASES_DAVIS_ATIVAS


def _fase_torneio_regular_ativa(fase):
    return fase in FASES_TORNEIO_ATIVAS


def _tratar_estado_torneio_corrompido(nome_save, caminho_torneio):
    print(
        "\n⚠️ Estado do torneio corrompido. Removendo arquivo e retornando ao menu principal..."
    )
    try:
        os.remove(caminho_torneio)
        return True
    except OSError as e:
        print(f"❌ Erro ao remover o arquivo do torneio corrompido: {e}")
        log_erro(
            nome_save,
            "remover_torneio_corrompido",
            e,
            {"caminho_torneio": caminho_torneio},
        )
        return False


def _estado_deve_ser_ignorado(estado, jogador_nome):
    return not _estado_pertence_ao_jogador(estado, jogador_nome)


def _finalizar_competicao_equipes(
    jogador_inst, nome_save, caminho_torneio, estado, fase
):
    finalizacao = _get_estado_finalizacao(estado)

    _executar_etapa_finalizacao(
        nome_save,
        jogador_inst.genero,
        estado,
        finalizacao,
        "davis_pontos_distribuidos",
        lambda: distribuir_pontos_davis(nome_save),
    )

    def _avancar_semana_davis():
        from src.calendario import avancar_semana

        avancar_semana(nome_save)

    _executar_etapa_finalizacao(
        nome_save,
        jogador_inst.genero,
        estado,
        finalizacao,
        "semana_avancada",
        _avancar_semana_davis,
    )

    jogador_inst = _recarregar_jogador_pos_semana(
        jogador_inst,
        nome_save,
        fase=fase,
        contexto_log="recarregar_jogador_davis_pos_avanco_semana",
    )

    _remover_arquivo_torneio(
        caminho_torneio,
        nome_save,
        fase,
        "remover_torneio_davis",
    )
    return jogador_inst


def _finalizar_torneio_regular(jogador_inst, nome_save, caminho_torneio, estado, fase):
    finalizacao = _get_estado_finalizacao(estado)

    _executar_etapa_finalizacao(
        nome_save,
        jogador_inst.genero,
        estado,
        finalizacao,
        "progressao_aplicada",
        lambda: _aplicar_progressao_natural_pos_torneio(
            jogador_inst, nome_save, estado
        ),
    )

    _executar_etapa_finalizacao(
        nome_save,
        jogador_inst.genero,
        estado,
        finalizacao,
        "pontos_distribuidos",
        lambda: distribuir_pontos_torneio(nome_save, genero=jogador_inst.genero),
    )

    if not finalizacao.get("entrevista_processada") and random.random() < 0.5:
        if (
            safe_input("\n🎙️ A imprensa quer falar com você. Dar entrevista? (s/n): ")
            .strip()
            .lower()
            == "s"
        ):
            venceu_torneio = fase == "final" and estado.get("jogador_vivo", True)
            disparar_entrevista(
                jogador_inst,
                info_torneio=estado,
                contexto="pos_jogo",
                fase=fase or "",
                venceu=venceu_torneio,
            )
        else:
            print("🗞️ Você recusou a entrevista desta semana.")
        _marcar_finalizacao_torneio(
            nome_save,
            jogador_inst.genero,
            estado,
            "entrevista_processada",
        )

    def _avancar_semana_regular():
        from src.calendario import avancar_semana

        avancar_semana(nome_save)

    _executar_etapa_finalizacao(
        nome_save,
        jogador_inst.genero,
        estado,
        finalizacao,
        "semana_avancada",
        _avancar_semana_regular,
    )

    jogador_inst = _recarregar_jogador_pos_semana(jogador_inst, nome_save, fase=fase)

    _remover_arquivo_torneio(
        caminho_torneio,
        nome_save,
        fase,
        "remover_torneio_finalizado",
    )
    return jogador_inst


def fluxo_principal(jogador_inst, nome_save, salvar_automaticamente=False):
    """
    Controlador principal que direciona o jogador para o menu apropriado.
    """
    while True:
        caminho_torneio = get_caminho_torneio_save(
            nome_save, genero=jogador_inst.genero
        )

        if not os.path.exists(caminho_torneio):
            # Não há torneio em andamento, vai para o menu principal (hub)
            sair_jogo = menu_principal(jogador_inst, nome_save, salvar_automaticamente)
            # Se o jogador sair do menu_principal (ex: com a opção "Sair"), o loop termina.
            if sair_jogo:
                break
            continue

        # Se existe um arquivo de torneio, vamos processá-lo.
        estado = carregar_estado_torneio(nome_save, genero=jogador_inst.genero)
        if estado is None:
            _tratar_estado_torneio_corrompido(nome_save, caminho_torneio)
            continue

        if _estado_deve_ser_ignorado(estado, jogador_inst.nome):
            # Ignora estados de torneio de simulação/NPC e segue para o hub.
            sair_jogo = menu_principal(jogador_inst, nome_save, salvar_automaticamente)
            if sair_jogo:
                break
            continue

        fase = estado.get("fase_atual")
        jogador_vivo = estado.get("jogador_vivo", True)
        tipo_torneio = estado.get("tipo", "")

        # Verifica se é competição por seleções (Davis/Billie Jean King Cup)
        if tipo_torneio in {"Davis Cup", "Billie Jean King Cup"}:
            jogador_convocado = estado.get("jogador_convocado", False)
            nome_competicao = tipo_torneio

            if jogador_vivo and jogador_convocado and _fase_davis_ativa(fase):
                resultado_davis = menu_davis(
                    jogador_inst,
                    nome_save,
                    salvar_automaticamente=salvar_automaticamente,
                )
                if resultado_davis == "saiu":
                    sair_jogo = menu_principal(
                        jogador_inst, nome_save, salvar_automaticamente
                    )
                    if sair_jogo:
                        break
                continue
            else:
                # Davis Cup terminou ou jogador não foi convocado/eliminado
                if not jogador_convocado:
                    print(
                        f"\n⚠️ Você não foi convocado para a {nome_competicao} desta semana — retornando ao calendário..."
                    )
                elif not jogador_vivo:
                    print(
                        f"\n🟥 Sua seleção foi eliminada da {nome_competicao} — retornando ao calendário..."
                    )
                else:
                    print(
                        f"\n🏁 {nome_competicao} concluída — retornando ao calendário..."
                    )

                jogador_inst = _finalizar_competicao_equipes(
                    jogador_inst,
                    nome_save,
                    caminho_torneio,
                    estado,
                    fase,
                )
                continue

        if jogador_vivo and _fase_torneio_regular_ativa(fase):
            # Recarrega o jogador para garantir que status de lesão/fadiga está atualizado.
            from src.jogador import carregar_jogador as _reload_jogador

            jogador_inst = _reload_jogador(nome_save) or jogador_inst
            resultado = menu_torneio(
                jogador_inst, nome_save, salvar_automaticamente=salvar_automaticamente
            )
            if resultado == "saiu":
                # Jogador saiu manualmente — vai ao menu principal sem encerrar o torneio
                sair_jogo = menu_principal(
                    jogador_inst, nome_save, salvar_automaticamente
                )
                if sair_jogo:
                    break
            continue
        else:
            # O torneio terminou ou o jogador foi eliminado.
            if not jogador_vivo:
                print(
                    "\n🟥 Você foi eliminado do torneio. Avançando para a próxima semana..."
                )
            else:
                print("\n🏁 Torneio concluído. Avançando para a próxima semana...")

            jogador_inst = _finalizar_torneio_regular(
                jogador_inst,
                nome_save,
                caminho_torneio,
                estado,
                fase,
            )

            # Após finalizar o torneio, o loop vai continuar e, como o arquivo não existe mais,
            # ele vai chamar o menu_principal na próxima iteração.
            continue
