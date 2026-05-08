import json
import logging
import os
import re
import shutil
from urllib.parse import unquote
from src.utils.log_jogo import log_erro
from src.utils.json_utils import salvar_json_seguro
from src.constants.torneio_constants import START_YEAR

try:
    from pydantic import ValidationError
except ImportError:
    class ValidationError(Exception):
        """Fallback para ambientes de teste que stubam apenas BaseModel."""

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "db")
SAVES_DIR = os.path.join(BASE_DIR, "saves")

_PATTERN_URL_ENCODED = re.compile(r"%(?:[0-9A-Fa-f]{2})")
_SAVE_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,32}$")


def validar_nome_save(nome: str) -> str:
    """Valida o nome do save contra caracteres perigosos e path traversal."""
    if not isinstance(nome, str):
        raise ValueError(f"Nome de save deve ser string, recebeu {type(nome)}")
    if not _SAVE_NAME_RE.match(nome):
        raise ValueError(
            f"Nome de save inválido: {nome!r}. Use apenas letras, números, _ e - (máx 32)."
        )
    # Garantir que o path resultante está dentro de SAVES_DIR
    caminho = os.path.abspath(os.path.join(SAVES_DIR, nome))
    if not caminho.startswith(os.path.abspath(SAVES_DIR)):
        raise ValueError("Path traversal detectado")
    return nome


def _decode_url_like(valor):
    if not isinstance(valor, str):
        return valor
    if not _PATTERN_URL_ENCODED.search(valor):
        return valor
    try:
        return unquote(valor)
    except Exception:
        return valor


def _sanitizar_nomes_urlencoded(obj, chave=None):
    """
    Decodifica nomes com URL encoding (%xx) em estruturas JSON de ranking/torneio.
    Mantém os dados originais quando não há padrão URL-encoded.
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = _sanitizar_nomes_urlencoded(v, chave=k)
        return out
    if isinstance(obj, list):
        return [_sanitizar_nomes_urlencoded(v, chave=chave) for v in obj]
    # Em confrontos serializados como listas/tuplas, os nomes podem vir sem chave
    # semântica (apenas strings em posições). Decodificamos qualquer string %xx.
    if isinstance(obj, str):
        return _decode_url_like(obj)
    return obj


# --- Nacionalidades ---


def carregar_nacionalidades():
    """Carrega o dicionário de nacionalidades do arquivo JSON."""
    caminho_para_arquivo = os.path.join(DB_DIR, "nacionalidades.json")
    try:
        with open(caminho_para_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Erro ao ler nacionalidades: %s", e)
        log_erro(None, "carregar_nacionalidades", e, {"arquivo": caminho_para_arquivo})
        return {}


def carregar_patrocinadores():
    """Carrega o dicionário de patrocinadores do arquivo JSON."""
    caminho_para_arquivo = os.path.join(DB_DIR, "sponsors.json")
    try:
        with open(caminho_para_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_erro(None, "carregar_patrocinadores", e, {"arquivo": caminho_para_arquivo})
        return {}


def carregar_staff():
    """Carrega o dicionário de profissionais e empresários do arquivo JSON."""
    caminho_para_arquivo = os.path.join(DB_DIR, "staff.json")
    try:
        with open(caminho_para_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_erro(None, "carregar_staff", e, {"arquivo": caminho_para_arquivo})
        return {"professionals": {}, "agents": {}}


def carregar_doencas():
    """Carrega o dicionário de doenças do arquivo JSON."""
    caminho_para_arquivo = os.path.join(DB_DIR, "diseases.json")
    try:
        with open(caminho_para_arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_erro(None, "carregar_doencas", e, {"arquivo": caminho_para_arquivo})
        return {}


# --- Caminhos (Paths) ---


def get_caminho_ranking_save(nome_save, genero="masculino"):
    """Índice Lean de simples do save. saves/<nome>/rankings/singles_{atp|wta}.json"""
    nome_save = validar_nome_save(nome_save)
    filename = "singles_atp.json" if genero == "masculino" else "singles_wta.json"
    return os.path.join(SAVES_DIR, nome_save, "rankings", filename)


def get_caminho_ranking_duplas(nome_save, genero="masculino"):
    """Índice Lean de duplas do save. saves/<nome>/rankings/doubles_{atp|wta}.json"""
    nome_save = validar_nome_save(nome_save)
    filename = "doubles_atp.json" if genero == "masculino" else "doubles_wta.json"
    return os.path.join(SAVES_DIR, nome_save, "rankings", filename)


def get_caminho_calendario_save(nome_save, genero="masculino", nome_torneio=None):
    """Retorna o caminho para o diretório de calendário sharded ou um torneio específico."""
    nome_save = validar_nome_save(nome_save)
    subfolder = "atp" if genero == "masculino" else "wta"
    base_path = os.path.join(SAVES_DIR, nome_save, "calendario", subfolder)
    if nome_torneio:
        safe_name = (
            nome_torneio.lower().replace(" ", "_").replace("'", "").replace(".", "")
        )
        return os.path.join(base_path, f"{safe_name}.json")
    return base_path


def get_caminho_ranking_global(genero="masculino"):
    """Retorna o caminho para o template de índice de NPCs (semente ao criar saves)."""
    filename = "npc_index_atp.json" if genero == "masculino" else "npc_index_wta.json"
    return os.path.join(DB_DIR, "templates", filename)


def get_caminho_ranking_global_duplas(genero="masculino"):
    """Retorna o caminho para o template de índice de duplas (semente ao criar saves)."""
    filename = (
        "npc_index_atp_duplas.json"
        if genero == "masculino"
        else "npc_index_wta_duplas.json"
    )
    return os.path.join(DB_DIR, "templates", filename)


def get_caminho_calendario(genero="masculino"):
    """Retorna o caminho para o arquivo de calendário."""
    filename = "calendario.json" if genero == "masculino" else "calendario_wta.json"
    return os.path.join(DB_DIR, filename)


def get_caminho_jogador_save(nome_save):
    """Retorna o caminho para o arquivo do jogador em um save específico."""
    nome_save = validar_nome_save(nome_save)
    return os.path.join(SAVES_DIR, nome_save, "jogador.json")


def get_caminho_temporada(nome_save):
    """Retorna o caminho para o arquivo de temporada de um save específico."""
    nome_save = validar_nome_save(nome_save)
    return os.path.join(SAVES_DIR, nome_save, "temporada.json")


def get_caminho_historico(nome_save):
    """Retorna o caminho para o histórico de campeões de um save."""
    nome_save = validar_nome_save(nome_save)
    return os.path.join(SAVES_DIR, nome_save, "historico.json")


def get_caminho_ranking_nacoes_davis():
    """Retorna o caminho para o ranking de nações da Davis Cup."""
    return os.path.join(DB_DIR, "ranking_nacoes_davis.json")


def carregar_json(caminho: str, padrao=None, model=None):
    """Lê um arquivo JSON com tratamento de erro e retorna os dados ou um valor padrão."""
    if not os.path.exists(caminho):
        return padrao

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
            if model:
                return validate_data(data, model)
            return data
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Erro ao ler JSON em %s. Tentando backup...", caminho)
        log_erro(None, "carregar_json", e, {"arquivo": caminho})

        # Tentar backup (.bak)
        backup = f"{caminho}.bak"
        if os.path.exists(backup):
            try:
                with open(backup, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if model:
                        return validate_data(data, model)
                    return data
            except Exception:
                pass
        return padrao


def validate_data(data, model):
    """Valida dados contra um modelo Pydantic, retornando o dict validado ou logando erro."""
    try:
        if isinstance(data, list):
            # No caso de listas (como rankings), validamos cada item.
            # Retornamos os objetos validados convertidos em dict.
            return [model.model_validate(item).model_dump() for item in data]
        return model.model_validate(data).model_dump()
    except ValidationError as e:
        logger.error("Erro de validação: %s", e)
        return data


def carregar_jogador(nome_save: str):
    """Carrega os dados do jogador de um save e retorna uma instância de Jogador."""
    nome_save = validar_nome_save(nome_save)
    caminho = get_caminho_jogador_save(nome_save)

    from src.models.player import PlayerModel

    dados = carregar_json(caminho, model=PlayerModel)

    if not dados:
        logger.error("Dados do jogador não encontrados no save '%s'.", nome_save)
        return None

    # Import inline para evitar dependência circular
    from src.jogador import reidratar_jogador

    return reidratar_jogador(dados, nome_save)


# --- Carregadores de Dados (Data Loaders) ---


def carregar_historico(nome_save):
    nome_save = validar_nome_save(nome_save)
    caminho = get_caminho_historico(nome_save)
    if not os.path.exists(caminho):
        # Se não existe no save, tenta pegar o template do db
        caminho_template = os.path.join(DB_DIR, "historico.json")
        if os.path.exists(caminho_template):
            with open(caminho_template, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"campeoes": {}, "recordes": {}}

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_erro(None, "carregar_historico", e, {"arquivo": caminho})
        return {"campeoes": {}, "recordes": {}}


def carregar_ranking(caminho):
    """Carrega um arquivo de ranking (JSON) de um caminho específico."""
    if not os.path.exists(caminho):
        return []  # Retorna uma lista vazia se o ranking não existir

    from src.models.ranking import RankingEntry

    data = carregar_json(caminho, model=RankingEntry)
    if data:
        return _sanitizar_nomes_urlencoded(data)
    return []


def get_caminho_torneio_save(nome_save, genero="masculino"):
    nome_save = validar_nome_save(nome_save)
    """Retorna o caminho para o arquivo de estado de um torneio de um save."""
    filename = "torneio_atp.json" if genero == "masculino" else "torneio_wta.json"
    return os.path.join(SAVES_DIR, nome_save, filename)


def carregar_estado_torneio(nome_save, genero="masculino"):
    nome_save = validar_nome_save(nome_save)
    """Carrega o estado de um torneio de um save específico."""
    caminho = get_caminho_torneio_save(nome_save, genero)
    if not os.path.exists(caminho):
        return None  # Retorna None se o arquivo não existir
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
            return _sanitizar_nomes_urlencoded(data)
    except json.JSONDecodeError as e:
        logger.error("Erro ao ler estado do torneio %s: %s", nome_save, e)
        log_erro(
            nome_save,
            "carregar_estado_torneio",
            e,
            {"arquivo": caminho, "genero": genero},
        )
        return None


def carregar_calendario(genero="masculino"):
    """Carrega os dados do calendário do arquivo JSON."""
    caminho = get_caminho_calendario(genero)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Erro ao ler calendário: %s", e)
        log_erro(None, "carregar_calendario", e, {"arquivo": caminho, "genero": genero})
        return {}


def carregar_temporada(nome_save):
    nome_save = validar_nome_save(nome_save)
    """Carrega o estado da temporada (ano e semana) do save."""
    caminho = get_caminho_temporada(nome_save)
    if not os.path.exists(caminho):
        return {"ano": START_YEAR, "semana": 1}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_temporada(nome_save, data):
    nome_save = validar_nome_save(nome_save)
    """Salva o estado da temporada (ano e semana) no save."""
    caminho = get_caminho_temporada(nome_save)
    salvar_json_seguro(caminho, data)


def obter_torneios_da_semana(semana, genero="masculino"):
    calendario = carregar_calendario(genero=genero)
    return calendario.get(str(semana), [])


def obter_torneio_por_nome(semana, nome_torneio, genero="masculino"):
    torneios = obter_torneios_da_semana(semana, genero=genero)
    for torneio in torneios:
        if torneio.get("nome") == nome_torneio:
            return torneio
    return None


def carregar_ranking_nacoes_davis():
    """Carrega o ranking de nações da Davis Cup."""
    caminho = get_caminho_ranking_nacoes_davis()
    if not os.path.exists(caminho):
        return {"nations": []}
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("nations", [])
                return data
            if isinstance(data, list):
                return {"nations": data}
    except json.JSONDecodeError as e:
        logger.error("Erro ao ler ranking de nações Davis: %s", e)
        log_erro(None, "carregar_ranking_nacoes_davis", e, {"arquivo": caminho})
    return {"nations": []}


def get_caminho_npc_save(nome_save, nome_jogador, genero="masculino"):
    """
    Retorna o caminho para o arquivo JSON de um NPC.
    Prioridade 1: saves/<nome>/npcs/<tour>/<jogador>.json (NPC já modificado no save).
    Prioridade 2: db/master/<tour>/<jogador>.json (dados master, nunca alterados pelo jogo).
    """
    if nome_save is not None:
        nome_save = validar_nome_save(nome_save)
    subfolder = "atp" if genero == "masculino" else "wta"
    safe_name = nome_jogador.lower().replace(" ", "_").replace("'", "").replace(".", "")
    filename = f"{safe_name}.json"

    if nome_save:
        save_path = os.path.join(SAVES_DIR, nome_save, "jogadores", subfolder, filename)
        if os.path.exists(save_path):
            return save_path

    master_path = os.path.join(DB_DIR, "master", subfolder, filename)
    return master_path


def carregar_npc_detalhado(nome_save, nome_jogador, genero="masculino"):
    """Carrega os dados completos de um NPC buscando no save ou no master DB."""
    if nome_save is not None:
        nome_save = validar_nome_save(nome_save)
    caminho = get_caminho_npc_save(nome_save, nome_jogador, genero)
    return carregar_json(caminho)


def listar_saves():
    """Retorna uma lista com os nomes de todos os saves existentes."""
    if not os.path.exists(SAVES_DIR):
        return []
    return [
        d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))
    ]


def excluir_save(nome_save):
    nome_save = validar_nome_save(nome_save)
    """Exclui permanentemente um save e todos os seus arquivos."""
    caminho = os.path.join(SAVES_DIR, nome_save)
    if os.path.exists(caminho):
        try:
            shutil.rmtree(caminho)
            return True
        except Exception as e:
            logger.error("Erro ao excluir o save '%s': %s", nome_save, e)
            return False
    return False
