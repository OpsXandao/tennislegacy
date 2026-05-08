import json
import re

def extract_sponsors():
    with open('src/patrocinios.py', 'r') as f:
        content = f.read()

    # Usar regex simples para capturar os dicionários de patrocinadores
    # Isso é um pouco arriscado, mas como os dados são bem estruturados, deve funcionar.
    # Alternativamente, podemos importar o módulo, mas ele tem dependências.
    
    # Vou tentar uma abordagem de importação "fake" para evitar problemas de dependência
    # mas como o código de dados é puro, talvez funcione.
    
    # Na verdade, vou usar o próprio Python para carregar os dados, 
    # mockando as dependências.
    
    d = {}
    # Mock src.constants.staff_constants.EMPRESARIOS_DISPONIVEIS
    class MockStaff:
        EMPRESARIOS_DISPONIVEIS = {}
    
    import sys
    from types import ModuleType
    
    mock_staff = ModuleType('src.constants.staff_constants')
    mock_staff.EMPRESARIOS_DISPONIVEIS = {}
    sys.modules['src.constants.staff_constants'] = mock_staff
    
    # Agora importamos o arquivo
    import src.patrocinios as pat
    
    # Salvar o dicionário final
    with open('db/sponsors.json', 'w') as f:
        json.dump(pat.PATROCINADORES_DISPONIVEIS, f, indent=4)

if __name__ == "__main__":
    extract_sponsors()
