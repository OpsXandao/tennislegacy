import os
from src.utils.json_utils import salvar_json_seguro
from src.dados import carregar_estado_torneio, get_caminho_torneio_save

def carregar_estado(nome_save: str, genero: str, default_factory=None):
    estado = carregar_estado_torneio(nome_save, genero=genero)
    if estado is None and default_factory:
        estado = default_factory()
        salvar_estado(nome_save, genero, estado)
    return estado

def salvar_estado(nome_save: str, genero: str, estado: dict):
    caminho = get_caminho_torneio_save(nome_save, genero=genero)
    salvar_json_seguro(caminho, estado)

def normalizar_agenda_dia(estado: dict) -> dict:
    if "agenda_dia" not in estado or not isinstance(estado["agenda_dia"], dict):
        estado["agenda_dia"] = {"dia_atual": 1, "jogos_realizados": []}
    return estado["agenda_dia"]

def virar_dia_torneio(estado: dict):
    agenda = normalizar_agenda_dia(estado)
    agenda["dia_atual"] += 1
    agenda["jogos_realizados"] = []
